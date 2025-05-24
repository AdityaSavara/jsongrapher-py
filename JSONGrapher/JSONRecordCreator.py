import json
#TODO: put an option to suppress warnings from JSONRecordCreator


#Start of the portion of the code for the GUI##
global_records_list = [] #This list holds onto records as they are added. Index 0 is the merged record. Each other index corresponds to record number (like 1 is first record, 2 is second record, etc)


#This is a JSONGrapher specific function
#That takes filenames and adds new JSONGrapher records to a global_records_list
#If the all_selected_file_paths and newest_file_name_and_path are [] and [], that means to clear the global_records_list.
def add_records_to_global_records_list_and_plot(all_selected_file_paths, newly_added_file_paths, plot_immediately=True):
    #First check if we have received a "clear" condition.
    if (len(all_selected_file_paths) == 0) and (len(newly_added_file_paths) == 0):
        global_records_list.clear()
        return global_records_list
    if len(global_records_list) == 0: #this is for the "first time" the function is called, but the newly_added_file_paths could be a list longer than one.
        first_record = create_new_JSONGrapherRecord()
        first_record.import_from_file(newly_added_file_paths[0]) #get first newly added record record.
        #index 0 will be the one we merge into.
        global_records_list.append(first_record)
        #index 1 will be where we store the first record, so we append again.
        global_records_list.append(first_record)
        #Now, check if there are more records.
        if len(newly_added_file_paths) > 1:
            for filename_and_path_index, filename_and_path in enumerate(newly_added_file_paths):
                if filename_and_path_index == 0:
                    pass #passing because we've already added first file.
                else:
                    current_record = create_new_JSONGrapherRecord() #make a new record
                    current_record.import_from_file(filename_and_path)        
                    global_records_list.append(current_record) #append it to global records list
                    global_records_list[0] = merge_JSONGrapherRecords([global_records_list[0], current_record]) #merge into the main record of records list, which is at index 0.
    else: #For case that global_records_list already exists when funciton is called.
        for filename_and_path_index, filename_and_path in enumerate(newly_added_file_paths):
            current_record = create_new_JSONGrapherRecord() #make a new record
            current_record.import_from_file(filename_and_path)        
            global_records_list.append(current_record) #append it to global records list
            global_records_list[0] = merge_JSONGrapherRecords([global_records_list[0], current_record]) #merge into the main record of records list, which is at index 0.
    if plot_immediately:
        #plot the index 0, which is the most up to date merged record.
        global_records_list[0].plot_with_plotly()
    json_string_for_download = json.dumps(global_records_list[0].fig_dict, indent=4)
    return [json_string_for_download] #For the GUI, this function should return a list with something convertable to string to save to file, in index 0.



#This ia JSONGrapher specific wrapper function to drag_and_drop_gui create_and_launch.
#This launches the python based JSONGrapher GUI.
def launch():
    #Check if we have the module we need. First try with package, then locally.
    try:
        import JSONGrapher.drag_and_drop_gui as drag_and_drop_gui
    except:
        #if the package is not present, or does not have it, try getting the module locally.
        import drag_and_drop_gui
    selected_files = drag_and_drop_gui.create_and_launch(app_name = "JSONGrapher", function_for_after_file_addition=add_records_to_global_records_list_and_plot)
    #We will not return the selected_files, and instead will return the global_records_list.
    return global_records_list

## End of the portion of the code for the GUI##


#the function create_new_JSONGrapherRecord is intended to be "like" a wrapper function for people who find it more
# intuitive to create class objects that way, this variable is actually just a reference 
# so that we don't have to map the arguments.
def create_new_JSONGrapherRecord(hints=False):
    #we will create a new record. While we could populate it with the init,
    #we will use the functions since it makes thsi function a bit easier to follow.
    new_record = JSONGrapherRecord()
    if hints == True:
        new_record.add_hints()
    return new_record

#This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
def load_JSONGrapherRecords(recordsList):
    return merge_JSONGrapherRecords(recordsList)

#This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
def import_JSONGrapherRecords(recordsList):
    return merge_JSONGrapherRecords(recordsList)

#This is a function for merging JSONGrapher records.
#recordsList is a list of records 
#Each record can be a JSONGrapherRecord object (a python class object) or a dictionary (meaning, a JSONGrapher JSON as a dictionary)
#If a record is received that is a string, then the function will attempt to convert that into a dictionary.
#The units used will be that of the first record encountered
#if changing this function's arguments, then also change those for load_JSONGrapherRecords and import_JSONGrapherRecords
def merge_JSONGrapherRecords(recordsList):
    if type(recordsList) == type(""):
        recordsList = [recordsList]
    import copy
    recordsAsDictionariesList = []
    merged_JSONGrapherRecord = create_new_JSONGrapherRecord()
    #first make a list of all the records as dictionaries.
    for record in recordsList:
        if type(record) == type({}):
            recordsAsDictionariesList.append(record)
        elif type(record) == type("string"):
            new_record = create_new_JSONGrapherRecord()
            new_fig_dict = new_record.import_from_json(record)
            recordsAsDictionariesList.append(new_fig_dict)
        else: #this assumpes there is a JSONGrapherRecord type received. 
            record = record.fig_dict
            recordsAsDictionariesList.append(record)
    #next, iterate through the list of dictionaries and merge each data object together.
    #We'll use the the units of the first dictionary.
    #We'll put the first record in directly, keeping the units etc. Then will "merge" in the additional data sets.
    #Iterate across all records received.
    for dictionary_index, current_fig_dict in enumerate(recordsAsDictionariesList):
        if dictionary_index == 0: #this is the first record case. We'll use this to start the list and also gather the units.
            merged_JSONGrapherRecord.fig_dict = copy.deepcopy(recordsAsDictionariesList[0])
            first_record_x_label = recordsAsDictionariesList[0]["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            first_record_y_label = recordsAsDictionariesList[0]["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            first_record_x_units = separate_label_text_from_units(first_record_x_label)["units"]
            first_record_y_units = separate_label_text_from_units(first_record_y_label)["units"]
        else:
            #first get the units of this particular record.
            this_record_x_label = recordsAsDictionariesList[dictionary_index]["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            this_record_y_label = recordsAsDictionariesList[dictionary_index]["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            this_record_x_units = separate_label_text_from_units(this_record_x_label)["units"]
            this_record_y_units = separate_label_text_from_units(this_record_y_label)["units"]
            #now get the ratio of the units for this record relative to the first record.
            #if the units are identical, then just make the ratio 1.
            if this_record_x_units == first_record_x_units:
                x_units_ratio = 1
            else:
                x_units_ratio = get_units_scaling_ratio(this_record_x_units, first_record_x_units)
            if this_record_y_units == first_record_y_units:
                y_units_ratio = 1
            else:
                y_units_ratio = get_units_scaling_ratio(this_record_y_units, first_record_y_units)
            #A record could have more than one data series, but they will all have the same units.
            #Thus, we use a function that will scale all of the dataseries at one time.
            if (x_units_ratio == 1) and (y_units_ratio == 1): #skip scaling if it's not necessary.
                scaled_fig_dict = current_fig_dict
            else:
                scaled_fig_dict = scale_fig_dict_values(current_fig_dict, x_units_ratio, y_units_ratio)
            #now, add the scaled data objects to the original one.
            #This is fairly easy using a list extend.
            merged_JSONGrapherRecord.fig_dict["data"].extend(scaled_fig_dict["data"])
    return merged_JSONGrapherRecord


### Start of portion of the file that has functions for scaling data to the same units ###
#The below function takes two units strings, such as
#    "(((kg)/m))/s" and  "(((g)/m))/s"
# and then returns the scaling ratio of units_string_1 / units_string_2
# So in the above example, would return 1000.
#Could add "tag_characters"='<>' as an optional argument to this and other functions
#to make the option of other characters for custom units.
def get_units_scaling_ratio(units_string_1, units_string_2):
    # Ensure both strings are properly encoded in UTF-8
    units_string_1 = units_string_1.encode("utf-8").decode("utf-8")
    units_string_2 = units_string_2.encode("utf-8").decode("utf-8")
    #If the unit strings are identical, there is no need to go further.
    if units_string_1 == units_string_2:
        return 1
    import unitpy #this function uses unitpy.
    #Replace "^" with "**" for unit conversion purposes.
    #We won't need to replace back because this function only returns the ratio in the end.
    units_string_1 = units_string_1.replace("^", "**")
    units_string_2 = units_string_2.replace("^", "**")
    #For now, we need to tag µ symbol units as if they are custom units. Because unitpy doesn't support that symbol yet (May 2025)
    units_string_1 = tag_micro_units(units_string_1)
    units_string_2 = tag_micro_units(units_string_2)
    #Next, need to extract custom units and add them to unitpy
    custom_units_1 = extract_tagged_strings(units_string_1)
    custom_units_2 = extract_tagged_strings(units_string_2)
    for custom_unit in custom_units_1:
        add_custom_unit_to_unitpy(custom_unit)
    for custom_unit in custom_units_2:
        add_custom_unit_to_unitpy(custom_unit)
    #Now, remove the "<" and ">" and will put them back later if needed.
    units_string_1 = units_string_1.replace('<','').replace('>','')
    units_string_2 = units_string_2.replace('<','').replace('>','')
    try:
        #First need to make unitpy "U" object and multiply it by 1. 
        #While it may be possible to find a way using the "Q" objects directly, this is the way I found so far, which converts the U object into a Q object.
        units_object_converted = 1*unitpy.U(units_string_1)
        ratio_with_units_object = units_object_converted.to(units_string_2)
    except: #the above can fail if there are reciprocal units like 1/bar rather than (bar)**(-1), so we have an except statement that tries "that" fix if there is a failure.
        units_string_1 = convert_inverse_units(units_string_1)
        units_string_2 = convert_inverse_units(units_string_2)
        units_object_converted = 1*unitpy.U(units_string_1)
        try:
            ratio_with_units_object = units_object_converted.to(units_string_2)
        except KeyError as e:
            import sys
            print(f"Error during unit converion in get_units_scaling_ratio: Missing key {e}. Ensure all unit definitions are correctly set.", "Unit 1:", units_string_1, "Unit 2:", units_string_2)
        except ValueError as e:
            import sys
            print(f"Error during unit conversion in get_units_scaling_ratio: {e}. Make sure unit values are valid and properly formatted.", "Unit 1:", units_string_1, "Unit 2:", units_string_2)
        except Exception as e:
            import sys
            print(f"An unexpected error occurred in in get_units_scaling_ratio when trying to convert units: {e}. Double-check that your records have the same units.", "Unit 1:", units_string_1, "Unit 2:",units_string_2)

    ratio_with_units_string = str(ratio_with_units_object)
    ratio_only = ratio_with_units_string.split(' ')[0] #what comes out may look like 1000 gram/(meter second), so we split and take first part.
    ratio_only = float(ratio_only)
    return ratio_only #function returns ratio only. If function is later changed to return more, then units_strings may need further replacements.

def return_custom_units_markup(units_string, custom_units_list):
    """puts markup around custom units with '<' and '>' """
    sorted_custom_units_list = sorted(custom_units_list, key=len, reverse=True)
    #the units should be sorted from longest to shortest if not already sorted that way.
    for custom_unit in sorted_custom_units_list:
        units_string = units_string.replace(custom_unit, '<'+custom_unit+'>')
    return units_string

    #This function tags microunits.
    #However, because unitpy gives unexpected behavior with the microsymbol,
    #We are actually going to change them from "µm" to "<microfrogm>"
def tag_micro_units(units_string):
    # Unicode representations of micro symbols:
    # U+00B5 → µ (Micro Sign)
    # U+03BC → μ (Greek Small Letter Mu)
    # U+1D6C2 → 𝜇 (Mathematical Greek Small Letter Mu)
    # U+1D6C1 → 𝝁 (Mathematical Bold Greek Small Letter Mu)
    micro_symbols = ["µ", "μ", "𝜇", "𝝁"]
    # Check if any micro symbol is in the string
    if not any(symbol in units_string for symbol in micro_symbols):
        return units_string  # If none are found, return the original string unchanged
    import re
    # Construct a regex pattern to detect any micro symbol followed by letters
    pattern = r"[" + "".join(micro_symbols) + r"][a-zA-Z]+"
    # Extract matches and sort them by length (longest first)
    matches = sorted(re.findall(pattern, units_string), key=len, reverse=True)
    # Replace matches with custom unit notation <X>
    for match in matches:
        frogified_match = f"<microfrog{match[1:]}>"
        units_string = units_string.replace(match, frogified_match)
    return units_string

    #We are actually going to change them back to "µm" from "<microfrogm>"
def untag_micro_units(units_string):
    if "<microfrog" not in units_string:  # Check if any frogified unit exists
        return units_string
    import re
    # Pattern to detect the frogified micro-units
    pattern = r"<microfrog([a-zA-Z]+)>"
    # Replace frogified units with µ + the original unit suffix
    return re.sub(pattern, r"µ\1", units_string)

def add_custom_unit_to_unitpy(unit_string):
    import unitpy
    from unitpy.definitions.entry import Entry
    #need to put an entry into "bases" because the BaseSet class will pull from that dictionary.
    unitpy.definitions.unit_base.bases[unit_string] = unitpy.definitions.unit_base.BaseUnit(label=unit_string, abbr=unit_string,dimension=unitpy.definitions.dimensions.dimensions["amount_of_substance"])
    #Then need to make a BaseSet object to put in. Confusingly, we *do not* put a BaseUnit object into the base_unit argument, below. 
    #We use "mole" to avoid conflicting with any other existing units.
    base_unit =unitpy.definitions.unit_base.BaseSet(mole = 1)
    #base_unit = unitpy.definitions.unit_base.BaseUnit(label=unit_string, abbr=unit_string,dimension=unitpy.definitions.dimensions.dimensions["amount_of_substance"])
    new_entry = Entry(label = unit_string, abbr = unit_string, base_unit = base_unit, multiplier= 1)
    #only add the entry if it is missing. A duplicate entry would cause crashing later.
    #We can't use the "unitpy.ledger.get_entry" function because the entries have custom == comparisons
    # and for the new entry, it will also return a special NoneType that we can't easy check.
    # the structer unitpy.ledger.units is a list, but unitpy.ledger._lookup is a dictionary we can use
    # to check if the key for the new unit is added or not.
    if unit_string not in unitpy.ledger._lookup:
        unitpy.ledger.add_unit(new_entry) #implied return is here. No return needed.

def extract_tagged_strings(text):
    """Extracts tags surrounded by <> from a given string. Used for custom units.
       returns them as a list sorted from longest to shortest"""
    import re
    list_of_tags = re.findall(r'<(.*?)>', text)
    set_of_tags = set(list_of_tags)
    sorted_tags = sorted(set_of_tags, key=len, reverse=True)
    return sorted_tags

#This function is to convert things like (1/bar) to (bar)**(-1)
#It was written by copilot and refined by further prompting of copilot by testing.
#The depth is because the function works iteratively and then stops when finished.
def convert_inverse_units(expression, depth=100):
    import re
    # Patterns to match valid reciprocals while ignoring multiplied units, so (1/bar)*bar should be  handled correctly.
    patterns = [r"1/\((1/.*?)\)", r"1/([a-zA-Z]+)"]
    for _ in range(depth):
        new_expression = expression
        for pattern in patterns:
            new_expression = re.sub(pattern, r"(\1)**(-1)", new_expression)
        
        # Stop early if no more changes are made
        if new_expression == expression:
            break
        expression = new_expression
    return expression

#the below function takes in a fig_dict, as well as x and/or y scaling values.
#The function then scales the values in the data of the fig_dict and returns the scaled fig_dict.
def scale_fig_dict_values(fig_dict, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1):
    import copy
    scaled_fig_dict = copy.deepcopy(fig_dict)
    #iterate across the data objects inside, and change them.
    for data_index, dataseries in enumerate(scaled_fig_dict["data"]):
        dataseries = scale_dataseries_dict(dataseries, num_to_scale_x_values_by=num_to_scale_x_values_by, num_to_scale_y_values_by=num_to_scale_y_values_by)
        scaled_fig_dict[data_index] = dataseries #this line shouldn't be needed due to mutable references, but adding for clarity and to be safe.
    return scaled_fig_dict


def scale_dataseries_dict(dataseries_dict, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1):
    import numpy as np
    dataseries = dataseries_dict
    dataseries["x"] = list(np.array(dataseries["x"], dtype=float)*num_to_scale_x_values_by) #convert to numpy array for multiplication, then back to list.
    dataseries["y"] = list(np.array(dataseries["y"], dtype=float)*num_to_scale_y_values_by) #convert to numpy array for multiplication, then back to list.
    
    # Ensure elements are converted to standard Python types. 
    dataseries["x"] = [float(val) for val in dataseries["x"]] #This line written by copilot.
    dataseries["y"] = [float(val) for val in dataseries["y"]] #This line written by copilot.
    return dataseries_dict

### End of portion of the file that has functions for scaling data to the same units ###

## This is a special dictionary class that will allow a dictionary
## inside a main class object to be synchronized with the fields within it.
class SyncedDict(dict):
    """A dictionary that automatically updates instance attributes."""
    def __init__(self, owner):
        super().__init__()
        self.owner = owner  # Store reference to the class instance
    def __setitem__(self, key, value):
        """Update both dictionary and instance attribute."""
        super().__setitem__(key, value)  # Set in the dictionary
        setattr(self.owner, key, value)  # Sync with instance attribute


class JSONGrapherRecord:
    """
    This class enables making JSONGrapher records. Each instance represents a structured JSON record for a graph.
    One can optionally provide an existing JSONGrapher record during creation to pre-populate the object.
    One can manipulate the fig_dict inside, directly, using syntax like Record.fig_dict["comments"] = ...
    One can also use syntax like Record["comments"] = ...  as some 'magic' synchronizes fields directlyin the Record with fields in the fig_dict.
    However, developers should usually use the syntax like Record.fig_dict, internally, to avoid any referencing mistakes.


    Arguments & Attributes (all are optional):
        comments (str): Can be used to put in general description or metadata related to the entire record. Can include citation links. Goes into the record's top level comments field.
        datatype: The datatype is the experiment type or similar, it is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. This ends up being the datatype field of the full JSONGrapher file. Avoid using double underscores '__' in this field  unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field, rather than a dataype name.
        graph_title: Title of the graph or the dataset being represented.
        data_objects_list (list): List of data series dictionaries to pre-populate the record. These may contain 'simulate' fields in them to call javascript source code for simulating on the fly.
        simulate_as_added: Boolean. True by default. If true, any data series that are added with a simulation field will have an immediate simulation call attempt.
        x_data: Single series x data in a list or array-like structure. 
        y_data: Single series y data in a list or array-like structure.
        x_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
        y_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
        layout: A dictionary defining the layout of the graph, including axis titles,
                comments, and general formatting options.
    
    Methods:
        add_data_series: Adds a new data series to the record.
        add_data_series_as_equation: Adds a new equation to plot, which will be evaluated on the fly.
        set_layout: Updates the layout configuration for the graph.
        export_to_json_file: Saves the entire record (comments, datatype, data, layout) as a JSON file.
        populate_from_existing_record: Populates the attributes from an existing JSONGrapher record.
    """

    def __init__(self, comments="", graph_title="", datatype="", data_objects_list = None, simulate_as_added = True, evaluate_equations_as_added = True, x_data=None, y_data=None, x_axis_label_including_units="", y_axis_label_including_units ="", plot_type ="", layout={}, existing_JSONGrapher_record=None):
        """
        Initialize a JSONGrapherRecord instance with optional attributes or an existing record.

            layout (dict): Layout dictionary to pre-populate the graph configuration.
            existing_JSONGrapher_record (dict): Existing JSONGrapher record to populate the instance.
        """  

        # Assign self.fig_dict in a way that it will push any changes to it into the class instance.
        self.fig_dict = SyncedDict(self)

        # If receiving a data_objects_list, validate it.
        if data_objects_list:
            validate_plotly_data_list(data_objects_list)  # Call a function from outside the class.

        # If receiving axis labels, validate them.
        if x_axis_label_including_units:
            validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=False)
        if y_axis_label_including_units:
            validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=False)

        self.fig_dict = {
            "comments": comments,  # Top-level comments
            "datatype": datatype,  # Top-level datatype (datatype)
            "data": data_objects_list if data_objects_list else [],  # Data series list
            "layout": layout if layout else {
                "title": {"text": graph_title},
                "xaxis": {"title": {"text": x_axis_label_including_units}},
                "yaxis": {"title": {"text": y_axis_label_including_units}}
            }
        }

        if simulate_as_added:  # Will try to simulate, but because this is the default, will use a try-except rather than crash the program.
            try:
                self.fig_dict = simulate_as_needed_in_fig_dict(self.fig_dict)
            except:
                pass

        if evaluate_equations_as_added:  # Will try to evaluate, but because this is the default, will use a try-except rather than crash the program.
            try:
                self.fig_dict = evaluate_equations_as_needed_in_fig_dict(self.fig_dict)
            except:
                pass

        self.plot_type = plot_type  # The plot_type is normally a series-level attribute.
        # However, if somebody sets the plot_type at the record level, we will use that plot_type for all the individual series.
        if plot_type != "":
            self.fig_dict["plot_type"] = plot_type

        # Populate attributes if an existing JSONGrapher record is provided as a dictionary.
        if existing_JSONGrapher_record:
            self.populate_from_existing_record(existing_JSONGrapher_record)

        # Initialize the hints dictionary, for use later, since the actual locations in the JSONRecord can be non-intuitive.
        self.hints_dictionary = {}
        # Adding hints. Here, the keys are the full field locations within the record.
        self.hints_dictionary["['comments']"] = "Use Record.set_comments() to populate this field. Can be used to put in a general description or metadata related to the entire record. Can include citations and links. Goes into the record's top-level comments field."
        self.hints_dictionary["['datatype']"] = "Use Record.set_datatype() to populate this field. This is the datatype, like experiment type, and is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. Avoid using double underscores '__' in this field unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field rather than a datatype name."
        self.hints_dictionary["['layout']['title']['text']"] = "Use Record.set_graph_title() to populate this field. This is the title for the graph."
        self.hints_dictionary["['layout']['xaxis']['title']['text']"] = "Use Record.set_x_axis_label() to populate this field. This is the x-axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets '< >'."  # x-axis label
        self.hints_dictionary["['layout']['yaxis']['title']['text']"] = "Use Record.set_y_axis_label() to populate this field. This is the y-axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets '< >'."

    #The __getitem__ and __setitem__ functions allow the class instance to behave 'like' a dictionary without using super.
    #The below functions allow the JSONGrapherRecord to populate the self.fig_dict each time something is added inside.
    #That is, if someone uses something like Record["comments"]="frog", it will also put that into self.fig_dict
    def __getitem__(self, key):
        """Allow access to attributes via self[key]"""
        return self.fig_dict.get(key, None)
    def __setitem__(self, key, value):
        """Redirect modifications of self[key] to self.fig_dict[key]"""
        self.fig_dict[key] = value

    #this function enables printing the current record.
    def __str__(self):
        """
        Returns a JSON-formatted string of the record with an indent of 4.
        """
        print("Warning: Printing directly will return the raw record without some automatic updates. It is recommended to use the syntax RecordObject.print_to_inspect() which will make automatic consistency updates and validation checks to the record before printing.")
        return json.dumps(self.fig_dict, indent=4)


    def add_data_series(self, series_name, x_values=[], y_values=[], simulate={}, simulate_as_added = True, comments="", trace_style="",  uid="", line="", extra_fields=None):
        """
        This is the normal way of adding an x,y data series.
        """
        # series_name: Name of the data series.
        # x: List of x-axis values. Or similar structure.
        # y: List of y-axis values. Or similar structure.
        # simulate: This is an optional field which, if used, is a JSON object with entries for calling external simulation scripts.
        # simulate_as_added: Boolean for calling simulation scripts immediately.
        # comments: Optional description of the data series.
        # trace_style: Type of the data (e.g., scatter, line, scatter_spline, spline, bar).
        # line: Dictionary describing line properties (e.g., shape, width).
        # uid: Optional unique identifier for the series (e.g., a DOI).
        # extra_fields: Dictionary containing additional fields to add to the series.
        x_values = list(x_values)
        y_values = list(y_values)

        data_series_dict = {
            "name": series_name,
            "x": x_values, 
            "y": y_values,
        }

        #Add optional inputs.
        if len(comments) > 0:
            data_series_dict["comments"] = comments
        if len(uid) > 0:
            data_series_dict["uid"] = uid
        if len(line) > 0:
            data_series_dict["line"] = line
        if len(trace_style) > 0:
            data_series_dict['trace_style'] = trace_style
        #add simulate field if included.
        if simulate:
            data_series_dict["simulate"] = simulate
        if simulate_as_added: #will try to simulate. But because this is the default, will use a try and except rather than crash program.
            try:
                data_series_dict = simulate_data_series(data_series_dict)
            except:
                pass
        # Add extra fields if provided, they will be added.
        if extra_fields:
            data_series_dict.update(extra_fields)
        #Add to the class object's data list.
        self.fig_dict["data"].append(data_series_dict) #implied return.
        return data_series_dict

    def add_data_series_as_equation(self, series_name, x_values=[], y_values=[], equation_dict={}, evaluate_equations_as_added = True, comments="", trace_style="",  uid="", line="", extra_fields=None):
        """
        This is a way to add an equation that would be used to fill an x,y data series.
        The equation will be a equation_dict of the json_equationer type
        """
        # series_name: Name of the data series.
        # x: List of x-axis values. Or similar structure.
        # y: List of y-axis values. Or similar structure.
        # equation_dict: This is the field for the equation_dict of json_equationer type
        # evaluate_equations_as_added: Boolean for evaluating equations immediately.
        # comments: Optional description of the data series.
        # plot_type: Type of the data (e.g., scatter, line).
        # line: Dictionary describing line properties (e.g., shape, width).
        # uid: Optional unique identifier for the series (e.g., a DOI).
        # extra_fields: Dictionary containing additional fields to add to the series.
        x_values = list(x_values)
        y_values = list(y_values)

        data_series_dict = {
            "name": series_name,
            "x": x_values, 
            "y": y_values,
        }

        #Add optional inputs.
        if len(comments) > 0:
            data_series_dict["comments"] = comments
        if len(uid) > 0:
            data_series_dict["uid"] = uid
        if len(line) > 0:
            data_series_dict["line"] = line
        if len(trace_style) > 0:
            data_series_dict['trace_style'] = trace_style
        #add equation field if included.
        if equation_dict:
            data_series_dict["equation"] = equation_dict
        # Add extra fields if provided, they will be added.
        if extra_fields:
            data_series_dict.update(extra_fields)
        #Add to the class object's data list.
        self.fig_dict["data"].append(data_series_dict)
        new_data_series_index = len(self.fig_dict["data"])-1 
        if evaluate_equations_as_added: #will try to simulate. But because this is the default, will use a try and except rather than crash program.
            try:
                self.fig_dict = evaluate_equation_for_data_series_by_index(self.fig_dict, new_data_series_index)
            except:
                pass
        ## Should consider adding "set_plot_type" for whole fig_dict, similar to what is in add_data_series


    def change_data_series_name(self, series_index, series_name):
        self.fig_dict["data"][series_index]["name"] = series_name


    #this function forces the re-simulation of a particular dataseries.
    #The simulator link will be extracted from the record, by default.
    def simulate_data_series_by_index(self, data_series_index, simulator_link='', verbose=False):
        self.fig_dict = simulate_specific_data_series_by_index(fig_dict=self.fig_dict, data_series_index=data_series_index, simulator_link=simulator_link, verbose=verbose)
        data_series_dict = self.fig_dict["data"][data_series_index] #implied return
        return data_series_dict #Extra regular return
    

    #this function returns the current record.
    def get_record(self):
        """
        Returns a JSON-dict string of the record
        """
        return self.fig_dict

    #The update_and_validate function will clean for plotly.
    def print_to_inspect(self, update_and_validate=True, validate=True, remove_remaining_hints=False):
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()
        print(json.dumps(self.fig_dict, indent=4))

    def populate_from_existing_record(self, existing_JSONGrapher_record):
        """
        Populates attributes from an existing JSONGrapher record.
        existing_JSONGrapher_record: A dictionary representing an existing JSONGrapher record.
        """
        #While we expect a dictionary, if a JSONGrapher ojbect is provided, we will simply pull the dictionary out of that.
        if type(existing_JSONGrapher_record) != type({}):
            existing_JSONGrapher_record = existing_JSONGrapher_record.fig_dict
        if type(existing_JSONGrapher_record) == type({}):
            if "comments" in existing_JSONGrapher_record:   self.fig_dict["comments"] = existing_JSONGrapher_record["comments"]
            if "datatype" in existing_JSONGrapher_record:      self.fig_dict["datatype"] = existing_JSONGrapher_record["datatype"]
            if "data" in existing_JSONGrapher_record:       self.fig_dict["data"] = existing_JSONGrapher_record["data"]
            if "layout" in existing_JSONGrapher_record:     self.fig_dict["layout"] = existing_JSONGrapher_record["layout"]

    #the below function takes in existin JSONGrpher record, and merges the data in.
    #This requires scaling any data as needed, according to units.
    def merge_in_JSONGrapherRecord(self, fig_dict_to_merge_in):
        import copy
        fig_dict_to_merge_in = copy.deepcopy(fig_dict_to_merge_in)
        if type(fig_dict_to_merge_in) == type({}):
            pass #this is what we are expecting.
        elif type(fig_dict_to_merge_in) == type("string"):
            fig_dict_to_merge_in = json.loads(fig_dict_to_merge_in)
        else: #this assumpes there is a JSONGrapherRecord type received. 
            fig_dict_to_merge_in = fig_dict_to_merge_in.fig_dict
        #Now extract the units of the current record.
        first_record_x_label = self.fig_dict["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
        first_record_y_label = self.fig_dict["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
        first_record_x_units = separate_label_text_from_units(first_record_x_label)["units"]
        first_record_y_units = separate_label_text_from_units(first_record_y_label)["units"]
        #Get the units of the new record.
        this_record_x_label = fig_dict_to_merge_in["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
        this_record_y_label = fig_dict_to_merge_in["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
        this_record_x_units = separate_label_text_from_units(this_record_x_label)["units"]
        this_record_y_units = separate_label_text_from_units(this_record_y_label)["units"]
        #now get the ratio of the units for this record relative to the first record.
        x_units_ratio = get_units_scaling_ratio(this_record_x_units, first_record_x_units)
        y_units_ratio = get_units_scaling_ratio(this_record_y_units, first_record_y_units)
        #A record could have more than one data series, but they will all have the same units.
        #Thus, we use a function that will scale all of the dataseries at one time.
        scaled_fig_dict = scale_fig_dict_values(fig_dict_to_merge_in, x_units_ratio, y_units_ratio)
        #now, add the scaled data objects to the original one.
        #This is fairly easy using a list extend.
        self.fig_dict["data"].extend(scaled_fig_dict["data"])


    
    def import_from_dict(self, fig_dict):
        self.fig_dict = fig_dict
    
    def import_from_file(self, json_filename_or_object):
        self.import_from_json(json_filename_or_object)

    #the json object can be a filename string or can be json object which is actually a dictionary.
    def import_from_json(self, json_filename_or_object):
        if type(json_filename_or_object) == type(""): #assume it's a json_string or filename_and_path.
            try:
                record = json.loads(json_filename_or_object) #first check if it's a json string.
            except json.JSONDecodeError as e1:  # Catch specific exception
                try:
                    import os
                    #if the filename does not exist, then we'll check if adding ".json" fixes the problem.
                    if not os.path.exists(json_filename_or_object):
                        json_added_filename = json_filename_or_object + ".json"
                        if os.path.exists(json_added_filename): json_filename_or_object = json_added_filename #only change the filename if the json_filename exists.
                    # Open the file in read mode with UTF-8 encoding
                    with open(json_filename_or_object, "r", encoding="utf-8") as file:
                        # Read the entire content of the file
                        record = file.read().strip()  # Stripping leading/trailing whitespace
                        self.fig_dict = json.loads(record)
                        return self.fig_dict
                except json.JSONDecodeError as e2:  # Catch specific exception
                    print(f"JSON loading failed on record: {record}. Error: {e1} when trying to parse as a json directly, and {e2} when trying to use as a filename. You may want to try opening your JSON file in VS Code or in an online JSON Validator. Does your json have double quotes around strings? Single quotes around strings is allowed in python, but disallowed in JSON specifications. You may also need to check how Booleans and other aspects are defined in JSON.")  # Improved error reporting
        else:
            self.fig_dict = json_filename_or_object
            return self.fig_dict

    def set_trace_style_one_data_series(self, data_series_index, trace_style):
         self.fig_dict['data'][data_series_index]["trace_style"] = trace_style
         return self.fig_dict['data'][data_series_index]

    def set_trace_styles_collection(self, trace_styles_collection):
        """
        Sets the plot_type field for the all data series.
        options are: scatter, spline, scatter_spline
        """
        self.plot_type["trace_styles_collection"] = trace_styles_collection

    def set_trace_style_all_series(self, trace_style):
        """
        Sets the plot_type field for the all data series.
        options are: scatter, spline, scatter_spline
        """
        for data_series_index in range(len(self.fig_dict['data'])): #works with array indexing.
            self.set_trace_style_one_data_series(data_series_index, trace_style)
  
    def set_datatype(self, datatype):
        """
        Sets the datatype field used as the experiment type or schema identifier.
            datatype (str): The new data type to set.
        """
        self.fig_dict['datatype'] = datatype

    def set_comments(self, comments):
        """
        Updates the comments field for the record.
            str: The updated comments value.
        """
        self.fig_dict['comments'] = comments

    def set_graph_title(self, graph_title):
        """
        Updates the title of the graph in the layout dictionary.
        graph_title (str): The new title to set for the graph.
        """
        self.fig_dict['layout']['title']['text'] = graph_title

    def set_x_axis_label_including_units(self, x_axis_label_including_units, remove_plural_units=True):
        """
        Updates the title of the x-axis in the layout dictionary.
        xaxis_title (str): The new title to set for the x-axis.
        """
        if "xaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("xaxis"), dict):
            self.fig_dict['layout']["xaxis"] = {}  # Initialize x-axis as a dictionary if it doesn't exist.
        validation_result, warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["xaxis"]["title"]['text'] = x_axis_label_including_units

    def set_y_axis_label_including_units(self, y_axis_label_including_units, remove_plural_units=True):
        """
        Updates the title of the y-axis in the layout dictionary.
        yaxis_title (str): The new title to set for the y-axis.
        """
        if "yaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("yaxis"), dict):
            self.fig_dict['layout']["yaxis"] = {}  # Initialize y-axis as a dictionary if it doesn't exist.
        
        validation_result, warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["yaxis"]["title"]['text'] = y_axis_label_including_units
    
    #function to set the min and max of the x axis in plotly way.
    def set_x_axis_range(self, min, max):
        self.fig_dict["layout"]["xaxis"][0] = min
        self.fig_dict["layout"]["xaxis"][1] = max
    #function to set the min and max of the y axis in plotly way.
    def set_y_axis_range(self, min, max):
        self.fig_dict["layout"]["yaxis"][0] = min
        self.fig_dict["layout"]["yaxis"][1] = max

    #function to scale the values in the data series by arbitrary amounts.
    def scale_record(self, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1):
        self.fig_dict = scale_fig_dict_values(self.fig_dict, num_to_scale_x_values_by=num_to_scale_x_values_by, num_to_scale_y_values_by=num_to_scale_y_values_by)

    def set_layout_fields(self, comments="", graph_title="", x_axis_label_including_units="", y_axis_label_including_units="", x_axis_comments="",y_axis_comments="", remove_plural_units=True):
        # comments: General comments about the layout. Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # graph_title: Title of the graph.
        # xaxis_title: Title of the x-axis, including units.
        # xaxis_comments: Comments related to the x-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # yaxis_title: Title of the y-axis, including units.
        # yaxis_comments: Comments related to the y-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        
        validation_result, warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)              
        validation_result, warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["title"]['text'] = graph_title
        self.fig_dict['layout']["xaxis"]["title"]['text'] = x_axis_label_including_units
        self.fig_dict['layout']["yaxis"]["title"]['text'] = y_axis_label_including_units
        

        #populate any optional fields, if provided:
        if len(comments) > 0:
            self.fig_dict['layout']["comments"] = comments
        if len(x_axis_comments) > 0:
            self.fig_dict['layout']["xaxis"]["comments"] = x_axis_comments
        if len(y_axis_comments) > 0:
            self.fig_dict['layout']["yaxis"]["comments"] = y_axis_comments     


        return self.fig_dict['layout']
    
    #This function validates the output before exporting, and also has an option of removing hints.
    #The update_and_validate function will clean for plotly.
    #simulate all series will simulate any series as needed.
    def export_to_json_file(self, filename, update_and_validate=True, validate=True, simulate_all_series = True, remove_simulate_fields= False, remove_remaining_hints=False):
        """
        writes the json to a file
        returns the json as a dictionary.
        update_and_validate function will clean for plotly. One can alternatively only validate.
        optionally simulates all series that have a simulate field (does so by default)
        optionally removes simulate filed from all series that have a simulate field (does not do so by default)
        optionally removes hints before export and return.
        """
        #if simulate_all_series is true, we'll try to simulate any series that need it, then clean the simulate fields out if requested.
        if simulate_all_series == True:
            self.fig_dict = simulate_as_needed_in_fig_dict(self.fig_dict)
        if remove_simulate_fields == True:
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate'])
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()

        # filepath: Optional, filename with path to save the JSON file.       
        if len(filename) > 0: #this means we will be writing to file.
            # Check if the filename has an extension and append `.json` if not
            if '.json' not in filename.lower():
                filename += ".json"
            #Write to file using UTF-8 encoding.
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.fig_dict, f, indent=4)
        return self.fig_dict

    ## Start of class functions related to getting actual graph objects and making plot images ##
    def get_plotly_fig(self, plot_style = {"layout_style":"", "trace_styles_collection":""}, update_and_validate=True, simulate_all_series = True, evaluate_all_equations = True, adjust_implicit_data_ranges=True):
        """
        Generates a Plotly figure from the stored fig_dict, performing simulations and equations as needed.
        By default, it will apply the default still hard coded into jsongrapher.

        Args:
            plot_style: String or dictionary of style to apply. Use '' to skip applying a style, or provide a list of length two containing both a layout style and a data series style."none" removes all style.
            simulate_all_series (bool): If True, performs simulations for all applicable series.
            update_and_validate (bool): If True, applies automatic corrections to fig_dict.
            evaluate_all_equations (bool): If True, evaluates all equation-based series.
            adjust_implicit_data_ranges (bool): If True, modifies ranges for implicit data series.

        Returns:
            plotly Figure: A validated Plotly figure object based on fig_dict.
        """
        import plotly.io as pio
        import copy
        if plot_style == {"layout_style":"", "trace_styles_collection":""}: #if the plot_style received is the default, we'll check if the fig_dict has a plot_style.
            plot_style = self.fig_dict.get("plot_style", {"layout_style":"", "trace_styles_collection":""}) #retrieve from self.fig_dict, and use defualt if not there.
        #This code *does not* simply modify self.fig_dict. It creates a deepcopy and then puts the final x y data back in.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=simulate_all_series, 
                                                                evaluate_all_equations=evaluate_all_equations, 
                                                                adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        #Regardless of implicit data series, we make a fig_dict copy, because we will clean self.fig_dict for creating the new plotting fig object.
        original_fig_dict = copy.deepcopy(self.fig_dict) 
        #before cleaning and validating, we'll apply styles.
        plot_style = parse_plot_style(plot_style=plot_style)
        self.apply_plot_style(plot_style=plot_style)
        #Now we clean out the fields and make a plotly object.
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record() #this is the line that cleans "self.fig_dict"
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate', 'custom_units_chevrons', 'equation', 'trace_style'])
        fig = pio.from_json(json.dumps(self.fig_dict))
        #restore the original fig_dict.
        self.fig_dict = original_fig_dict 
        return fig

    #Just a wrapper aroudn plot_with_plotly.
    def plot(self, plot_style = {"layout_style":"", "trace_styles_collection":""}, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
        return self.plot_with_plotly(plot_style=plot_style, update_and_validate=update_and_validate, simulate_all_series=simulate_all_series, evaluate_all_equations=evaluate_all_equations, adjust_implicit_data_ranges=adjust_implicit_data_ranges)

    #simulate all series will simulate any series as needed. If changing this function's arguments, also change those for self.plot()
    def plot_with_plotly(self, plot_style = {"layout_style":"", "trace_styles_collection":""}, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
        fig = self.get_plotly_fig(plot_style=plot_style,
                                  simulate_all_series=simulate_all_series, 
                                  update_and_validate=update_and_validate, 
                                  evaluate_all_equations=evaluate_all_equations, 
                                  adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        fig.show()
        #No need for fig.close() for plotly figures.


    #simulate all series will simulate any series as needed.
    def export_to_plotly_png(self, filename, simulate_all_series = True, update_and_validate=True, timeout=10):
        fig = self.get_plotly_fig(simulate_all_series = simulate_all_series, update_and_validate=update_and_validate)       
        # Save the figure to a file, but use the timeout version.
        self.export_plotly_image_with_timeout(plotly_fig = fig, filename=filename, timeout=timeout)

    def export_plotly_image_with_timeout(self, plotly_fig, filename, timeout=10):
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        import plotly.io as pio
        pio.kaleido.scope.mathjax = None
        fig = plotly_fig
        
        def export():
            try:
                fig.write_image(filename, engine="kaleido")
            except Exception as e:
                print(f"Export failed: {e}")

        import threading
        thread = threading.Thread(target=export, daemon=True)  # Daemon ensures cleanup
        thread.start()
        thread.join(timeout=timeout)  # Wait up to 10 seconds
        if thread.is_alive():
            print("Skipping Plotly png export: Operation timed out. Plotly image export often does not work from Python. Consider using export_to_matplotlib_png.")

    #update_and_validate will 'clean' for plotly. 
    #In the case of creating a matplotlib figure, this really just means removing excess fields.
    #simulate all series will simulate any series as needed.
    def get_matplotlib_fig(self, plot_style = {"layout_style":"", "trace_styles_collection":""}, update_and_validate=True, simulate_all_series = True, evaluate_all_equations = True, adjust_implicit_data_ranges=True):
        """
        Generates a matplotlib figure from the stored fig_dict, performing simulations and equations as needed.

        Args:
            simulate_all_series (bool): If True, performs simulations for applicable series.
            update_and_validate (bool): If True, applies automatic corrections to fig_dict.
            evaluate_all_equations (bool): If True, evaluates all equation-based series.
            adjust_implicit_data_ranges (bool): If True, modifies ranges for implicit data series.

        Returns:
            plotly Figure: A validated matplotlib figure object based on fig_dict.
        """
        import copy
        if plot_style == {"layout_style":"", "trace_styles_collection":""}: #if the plot_style received is the default, we'll check if the fig_dict has a plot_style.
            plot_style = self.fig_dict.get("plot_style", {"layout_style":"", "trace_styles_collection":""})
        #This code *does not* simply modify self.fig_dict. It creates a deepcopy and then puts the final x y data back in.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=simulate_all_series, 
                                                                evaluate_all_equations=evaluate_all_equations, 
                                                                adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        #Regardless of implicit data series, we make a fig_dict copy, because we will clean self.fig_dict for creating the new plotting fig object.
        original_fig_dict = copy.deepcopy(self.fig_dict) #we will get a copy, because otherwise the original fig_dict will be forced to be overwritten.    
        #before cleaning and validating, we'll apply styles.
        plot_style = parse_plot_style(plot_style=plot_style)
        self.apply_plot_style(plot_style=plot_style)
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate', 'custom_units_chevrons', 'equation', 'trace_style'])
        fig = convert_JSONGrapher_dict_to_matplotlib_fig(self.fig_dict)
        self.fig_dict = original_fig_dict #restore the original fig_dict.
        return fig

    #simulate all series will simulate any series as needed.
    def plot_with_matplotlib(self, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
        import matplotlib.pyplot as plt
        fig = self.get_matplotlib_fig(simulate_all_series=simulate_all_series, 
                                      update_and_validate=update_and_validate, 
                                      evaluate_all_equations=evaluate_all_equations, 
                                      adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        plt.show()
        plt.close(fig) #remove fig from memory.

    #simulate all series will simulate any series as needed.
    def export_to_matplotlib_png(self, filename, simulate_all_series = True, update_and_validate=True):
        import matplotlib.pyplot as plt
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        fig = self.get_matplotlib_fig(simulate_all_series = simulate_all_series, update_and_validate=update_and_validate)       
        # Save the figure to a file
        fig.savefig(filename)
        plt.close(fig) #remove fig from memory.

    ## End of class functions related to getting actual graph objects and making plot images ##

    def add_hints(self):
        """
        Adds hints to fields that are currently empty strings using self.hints_dictionary.
        Dynamically parses hint keys (e.g., "['layout']['xaxis']['title']") to access and update fields in self.fig_dict.
        The hints_dictionary is first populated during creation of the class object in __init__.
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".
            # Enumerate over keys starting with index 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length:
                    current_field = current_field.setdefault(current_path_key, {}) # `setdefault` will fill with the second argument if the requested field does not exist.
                else:
                    # Final key: if the field is empty, set it to hint_text.
                    if current_field.get(current_path_key, "") == "": # `get` will return the second argument if the requested field does not exist.
                        current_field[current_path_key] = hint_text
                        
    def remove_hints(self):
        """
        Removes hints by converting fields back to empty strings if their value matches the hint text in self.hints_dictionary.
        Dynamically parses hint keys (e.g., "['layout']['xaxis']['title']") to access and update fields in self.fig_dict.
        The hints_dictionary is first populated during creation of the class object in __init__.
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".  
            # Enumerate with a starting index of 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length: 
                    current_field = current_field.get(current_path_key, {})  # `get` will return the second argument if the requested field does not exist.
                else:
                    # Final key: if the field's value equals the hint text, reset it to an empty string.
                    if current_field.get(current_path_key, "") == hint_text:
                        current_field[current_path_key] = ""

    ## Start of class functions related to styles and formatting ##

    #Make some pointers to external functions, for convenience, so people can use syntax like record.function_name() if desired.
    # def apply_layout_style(self, layout_style_to_apply=''):
    #     self.fig_dict = apply_layout_style_to_plotly_dict(self.fig_dict, layout_style_to_apply=layout_style_to_apply)
    def set_layout_style(self, layout_style):
        #layout_style should be a dictionary or a string
        plot_style = self.fig_dict.get('plot_style',{})
        plot_style["layout_style"] = layout_style
        self.fig_dict["plot_style"] = plot_style
        return plot_style
    def remove_current_layout_style_setting(self):
        plot_style = self.fig_dict.get('plot_style',{})
        if "layout_style" in plot_style:
            plot_style.pop("layout_style")
        self.fig_dict["plot_style"] = plot_style
        return plot_style
    def set_trace_styles_collection(self, trace_styles_collection):
        #trace_styles_collection should be a dictionary or a string
        plot_style = self.fig_dict.get('plot_style',{})
        plot_style["trace_styles_collection"] = trace_styles_collection
        self.fig_dict["plot_style"] = plot_style
        return plot_style
    def remove_current_trace_styles_collection_setting(self):
        plot_style = self.fig_dict.get('plot_style',{})
        if "trace_styles_collection" in plot_style:
            plot_style.pop("trace_styles_collection")
        #adding in commmon misspelling cases.
        if "traces_style_collection" in plot_style:
            plot_style.pop("traces_style_collection")
        self.fig_dict["plot_style"] = plot_style
        return plot_style
    def set_trace_style_indvidiual_data_series(self, data_series_index, trace_style):
        #data_series_index should be an integer. trace_style should be a string.
        self.fig_dict["data"][data_series_index]["trace_style"] = trace_style
        return self.fig_dict["data"][data_series_index]
    def remove_current_trace_style_setting_indvidiual_data_series(self, data_series_index, trace_style):
        #data_series_index should be an integer. trace_style should be a string.
        if "trace_style" in self.fig_dict["data"][data_series_index]
            self.fig_dict["data"][data_series_index].pop("trace_style")
        return self.fig_dict["data"][data_series_index]
    # def apply_plot_style(self, plot_style= {"layout_style":"", "trace_styles_collection":""}): 
    #     #the plot_style can be a string, or a plot_style dictionary {"layout_style":"default", "trace_styles_collection":"default"} or a list of length two with those two items.
    #     #The plot_style dictionary can include a pair of dictionaries.
    #     #if apply style is called directly, we will first put the plot_style into the plot_style field
    #     #This way, the style will stay.
    #     self.fig_dict['plot_style'] = plot_style
    #     self.fig_dict = apply_plot_style_to_plotly_dict(self.fig_dict, plot_style=plot_style)
    # def remove_plot_style(self):
    #     self.fig_dict.pop("plot_style") #This line removes the field of plot_style from the fig_dict.
    #     self.fig_dict = remove_plot_style_from_plotly_dict(self.fig_dict) #This line removes the actual formatting from the fig_dict.
    # def remove_current_plot_style_setting(self):
    #     self.fig_dict.pop("plot_style") #This line removes the field of plot_style from the fig_dict.
    def extract_layout_style(self):
        layout_style = extract_layout_style_from_plotly_dict(self.fig_dict)
        return layout_style
    def apply_trace_style_by_index(self, data_series_index, trace_styles_collection='', trace_style=''):
        if trace_styles_collection == '':
            self.fig_dict.setdefault("plot_style",{}) #create the plot_style dictionary if it's not there. Else, return current value.
            trace_styles_collection = self.fig_dict["plot_style"].get("trace_styles_collection", '') #check if there is a trace_styles_collection within it, and use that. If it's not there, then use ''.
        #trace_style should be a dictionary, but can be a string.
        data_series = self.fig_dict["data"][data_series_index]
        data_series = apply_trace_style_to_single_data_series(data_series, trace_styles_collection=trace_styles_collection, trace_style_to_apply=trace_style) #this is the 'external' function, not the one in the class.
        self.fig_dict["data"][data_series_index] = data_series
        return data_series
    def extract_trace_styles_collection(self, new_trace_styles_collection_name='', indices_of_data_series_to_extract_styles_from=[], new_trace_style_names_list = []):
        fig_dict = self.fig_dict
        new_trace_styles_collection_dictionary = {}
        if new_trace_styles_collection_name == '':
            new_trace_styles_collection_name = 'replace_this_with_your_trace_styles_collection_name'
        if indices_of_data_series_to_extract_styles_from == []:
            indices_of_data_series_to_extract_styles_from = range(len(fig_dict["data"]))
        if new_trace_style_names_list == []:
            for data_series_index in indices_of_data_series_to_extract_styles_from:
                data_series_dict = fig_dict["data"][data_series_index]
                trace_style_name = data_series_dict.get('trace_style', '')  # return blank line if not there.
                if trace_style_name == '':
                    trace_style_name = 'custom_trace_style' + str(data_series_index)
                if trace_style_name not in new_trace_style_names_list:
                    pass
                else:
                    trace_style_name = trace_style_name + str(data_series_index)
                new_trace_style_names_list.append(trace_style_name)
        if len(indices_of_data_series_to_extract_styles_from) != len(new_trace_style_names_list):
            raise ValueError("Error: The input for indices_of_data_series_to_extract_styles_from is not compatible with the input for new_trace_style_names_list. There is a difference in lengths after the automatic parsing and filling that occurs.")
        for index_to_extract_from in indices_of_data_series_to_extract_styles_from:
            new_trace_style_name = new_trace_style_names_list[index_to_extract_from]
            extracted_trace_style = extract_trace_style_by_index(fig_dict, index_to_extract_from, new_trace_style_name=new_trace_style_names_list[index_to_extract_from])
            new_trace_styles_collection_dictionary[new_trace_style_name] = extracted_trace_style[new_trace_style_name]
        new_trace_styles_collection = {new_trace_styles_collection_name: new_trace_styles_collection_dictionary}
        return new_trace_styles_collection
    def export_trace_styles_collection(self, new_trace_styles_collection_name='', indices_of_data_series_to_extract_styles_from=[], new_trace_style_names_list = [], filename=''):
        new_trace_styles_collection = self.extract_trace_styles_collection(new_trace_styles_collection_name=new_trace_styles_collection_name, indices_of_data_series_to_extract_styles_from=indices_of_data_series_to_extract_styles_from, new_trace_style_names_list = new_trace_style_names_list)
        if new_trace_styles_collection_name == '':
            new_trace_styles_collection_name = list(new_trace_styles_collection.keys())[0] #the first key will contain the collection name.
        if filename == '':
            filename = new_trace_styles_collection_name
        export_trace_styles_collection(trace_styles_collection=new_trace_styles_collection, trace_styles_collection_name=new_trace_styles_collection_name, filename=filename)
    def extract_trace_style_by_index(self, data_series_index, new_trace_style_name=''):
        extracted_trace_style = extract_trace_style_by_index(self.fig_dict, data_series_index, new_trace_style_name=new_trace_style_name)
        return extracted_trace_style
    def export_trace_style_by_index(self, data_series_index, new_trace_style_name='', filename=''):
        extracted_trace_style = extract_trace_style_by_index(self.fig_dict, data_series_index, new_trace_style_name=new_trace_style_name)
        new_trace_style_name = list(extracted_trace_style.keys())[0] #the extracted_trace_style will have a single key which is the style name.
        if filename == '': 
            filename = new_trace_style_name
        export_trace_style(trace_style_dict=extracted_trace_style[new_trace_style_name],trace_style_name=new_trace_style_name, filename=filename)
        return extracted_trace_style       
    
    ## End of class functions related to styles and formatting ##
    
    def validate_JSONGrapher_record(self):
        validate_JSONGrapher_record(self)
    def update_and_validate_JSONGrapher_record(self):
        update_and_validate_JSONGrapher_record(self)


# helper function to validate x axis and y axis labels.
# label string will be the full label including units. Axis_name is typically "x" or "y"
def validate_JSONGrapher_axis_label(label_string, axis_name="", remove_plural_units=True):
    """
    Validates the axis label provided to JSONGrapher.

    Args:
        label_string (str): The axis label containing a numeric value and units.
        axis_name (str): The name of the axis being validated (e.g., 'x' or 'y').
        remove_plural_units (boolean) : Instructions wil to remove plural units or not. Will remove them in the returned stringif set to True, or will simply provide a warning if set to False.

    Returns:
        None: Prints warnings if any validation issues are found.
    """
    warnings_list = []
    #First check if the label is empty.
    if label_string == '':
        warnings_list.append(f"Your {axis_name} axis label is an empty string. JSONGrapher records should not have empty strings for axis labels.")
    else:    
        parsing_result = separate_label_text_from_units(label_string)  # Parse the numeric value and units from the label string
        # Check if units are missing
        if parsing_result["units"] == "":
            warnings_list.append(f"Your {axis_name} axis label is missing units. JSONGrapher is expected to handle axis labels with units, with the units between parentheses '( )'.")    
        # Check if the units string has balanced parentheses
        open_parens = parsing_result["units"].count("(")
        close_parens = parsing_result["units"].count(")")
        if open_parens != close_parens:
            warnings_list.append(f"Your {axis_name} axis label has unbalanced parentheses in the units. The number of opening parentheses '(' must equal the number of closing parentheses ')'.")
    
    #now do the plural units check.
    units_changed_flag, units_singularized = units_plural_removal(parsing_result["units"])
    if units_changed_flag == True:
        warnings_list.append("The units of " + parsing_result["units"] + " appear to be plural. Units should be entered as singular, such as 'year' rather than 'years'.")
        if remove_plural_units==True:
            label_string = parsing_result["text"] + " (" + units_singularized + ")"
            warnings_list.append("Now removing the 's' to change the units into singular '" + units_singularized + "'.  To avoid this change, use the function you've called with the optional argument of remove_plural_units set to False.")
    else:
        pass

    # Return validation result
    if warnings_list:
        print(f"Warning: Your  {axis_name} axis label did not pass expected vaidation checks. You may use Record.set_x_axis_label() or Record.set_y_axis_label() to change the labels. The validity check fail messages are as follows: \n", warnings_list)
        return False, warnings_list, label_string
    else:
        return True, [], label_string    
    
def units_plural_removal(units_to_check):
    """
    Parses a units string to remove "s" if the string is found as an exact match without an s in the units lists.
    Args:
        units_to_check (str): A string containing units to check.

    Returns:
        tuple: A tuple of two values
              - "changed" (Boolean): True, or False, where True means the string was changed to remove an "s" at the end.
              - "singularized" (string): The units parsed to be singular, if needed.
    """
    #Check if we have the module we need. If not, return with no change.
    try:
        import JSONGrapher.units_list as units_list
    except:
        #if JSONGrapher is not present, try getting the units_list file locally.
        try:
            import units_list
        except:#if still not present, give up and avoid crashing.
            units_changed_flag = False
            return units_changed_flag, units_to_check #return None if there was no test.

    #First try to check if units are blank or ends with "s" is in the units list. 
    if (units_to_check == "") or (units_to_check[-1] != "s"):
        units_changed_flag = False
        units_singularized = units_to_check #return if string is blank or does not end with s.
    elif (units_to_check != "") and (units_to_check[-1] == "s"): #continue if not blank and ends with s. 
        if (units_to_check in units_list.expanded_ids_set) or (units_to_check in units_list.expanded_names_set):#return unchanged if unit is recognized.
            units_changed_flag = False
            units_singularized = units_to_check #No change if was found.
        else:
            truncated_string = units_to_check[0:-1] #remove last letter.
            if (truncated_string in units_list.expanded_ids_set) or (truncated_string in units_list.expanded_names_set):
                units_changed_flag = True
                units_singularized = truncated_string #return without the s.   
            else: #No change if the truncated string isn't found.
                units_changed_flag = False
                units_singularized = units_to_check
    return units_changed_flag, units_singularized


def separate_label_text_from_units(label_with_units):
    """
    Parses a label with text string and units in parentheses after that to return the two parts.
    This is not meant to separate strings like "Time (s)", it is not meant for strings like "5 (kg)"

    Args:
        value (str): A string containing a label and optional units enclosed in parentheses.
                     Example: "Time (Years)" or "Speed (km/s)

    Returns:
        dict: A dictionary with two keys:
              - "text" (str): The label text parsed from the input string.
              - "units" (str): The units parsed from the input string, or an empty string if no units are present.
    """
    # Find the position of the first '(' and the last ')'
    start = label_with_units.find('(')
    end = label_with_units.rfind(')')
    
    # Ensure both are found and properly ordered
    if start != -1 and end != -1 and end > start:
        text_part = label_with_units[:start].strip()  # Everything before '('
        units_part = label_with_units[start + 1:end].strip()  # Everything inside '()'
    else:
        text_part = label_with_units
        units_part = ""
    parsed_output = {
                "text":text_part,
                "units":units_part
            }
    return parsed_output


def validate_plotly_data_list(data):
    """
    Validates the entries in a Plotly data array.
    If a dictionary is received, the function will assume you are sending in a single dataseries for validation
    and will put it in a list of one before the validation.

    Args:
        data (list): A list of dictionaries, each representing a Plotly trace.

    Returns:
        bool: True if all entries are valid, False otherwise.
        list: A list of errors describing why the validation failed.
    """
    #check if a dictionary was received. If so, will assume that
    #a single series has been sent, and will put it in a list by itself.
    if type(data) == type({}):
        data = [data]

    required_fields_by_type = {
        "scatter": ["x", "y"],
        "bar": ["x", "y"],
        "pie": ["labels", "values"],
        "heatmap": ["z"],
    }
    
    warnings_list = []

    for i, trace in enumerate(data):
        if not isinstance(trace, dict):
            warnings_list.append(f"Trace {i} is not a dictionary.")
            continue
        if "comments" in trace:
            warnings_list.append(f"Trace {i} has a comments field within the data. This is allowed by JSONGrapher, but is discouraged by plotly. By default, this will be removed when you export your record.")
        # Determine the type based on the fields provided
        trace_style = trace.get("type")
        if not trace_style:
            # Infer type based on fields and attributes
            if "x" in trace and "y" in trace:
                if "mode" in trace or "marker" in trace or "line" in trace:
                    trace_style = "scatter"
                elif "text" in trace or "marker.color" in trace:
                    trace_style = "bar"
                else:
                    trace_style = "scatter"  # Default assumption
            elif "labels" in trace and "values" in trace:
                trace_style = "pie"
            elif "z" in trace:
                trace_style = "heatmap"
            else:
                warnings_list.append(f"Trace {i} cannot be inferred as a valid type.")
                continue
        
        # Check for required fields
        required_fields = required_fields_by_type.get(trace_style, [])
        for field in required_fields:
            if field not in trace:
                warnings_list.append(f"Trace {i} (type inferred as {trace_style}) is missing required field: {field}.")

    if warnings_list:
        print("Warning: There are some entries in your data list that did not pass validation checks: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def parse_units(value):
    """
    Parses a numerical value and its associated units from a string. This meant for scientific constants and parameters
    Such as rate constants, gravitational constant, or simiilar.
    This function is not meant for separating the axis label from its units. For that, use  separate_label_text_from_units

    Args:
        value (str): A string containing a numeric value and optional units enclosed in parentheses.
                     Example: "42 (kg)" or "100".

    Returns:
        dict: A dictionary with two keys:
              - "value" (float): The numeric value parsed from the input string.
              - "units" (str): The units parsed from the input string, or an empty string if no units are present.
    """
    # Find the position of the first '(' and the last ')'
    start = value.find('(')
    end = value.rfind(')')
    # Ensure both are found and properly ordered
    if start != -1 and end != -1 and end > start:
        number_part = value[:start].strip()  # Everything before '('
        units_part = value[start + 1:end].strip()  # Everything inside '()'
        parsed_output = {
            "value": float(number_part),  # Convert number part to float
            "units": units_part  # Extracted units
        }
    else:
        parsed_output = {
            "value": float(value),  # No parentheses, assume the entire string is numeric
            "units": ""  # Empty string represents absence of units
        }
    
    return parsed_output

#This function does updating of internal things before validating
#This is used before printing and returning the JSON record.
def update_and_validate_JSONGrapher_record(record, clean_for_plotly=True):
    record.validate_JSONGrapher_record()
    if clean_for_plotly == True:
        record.fig_dict = clean_json_fig_dict(record.fig_dict)
    return record

#TODO: add the ability for this function to check against the schema.
def validate_JSONGrapher_record(record):
    """
    Validates a JSONGrapher record to ensure all required fields are present and correctly structured.

    Args:
        record (dict): The JSONGrapher record to validate.

    Returns:
        bool: True if the record is valid, False otherwise.
        list: A list of errors describing any validation issues.
    """
    warnings_list = []

    # Check top-level fields
    if not isinstance(record, dict):
        return False, ["The record is not a dictionary."]
    
    # Validate "comments"
    if "comments" not in record:
        warnings_list.append("Missing top-level 'comments' field.")
    elif not isinstance(record["comments"], str):
        warnings_list.append("'comments' is a recommended field and should be a string with a description and/or metadata of the record, and citation references may also be included.")
    
    # Validate "datatype"
    if "datatype" not in record:
        warnings_list.append("Missing 'datatype' field.")
    elif not isinstance(record["datatype"], str):
        warnings_list.append("'datatype' should be a string.")
    
    # Validate "data"
    if "data" not in record:
        warnings_list.append("Missing top-level 'data' field.")
    elif not isinstance(record["data"], list):
        warnings_list.append("'data' should be a list.")
        validate_plotly_data_list(record["data"]) #No need to append warnings, they will print within that function.
    
    # Validate "layout"
    if "layout" not in record:
        warnings_list.append("Missing top-level 'layout' field.")
    elif not isinstance(record["layout"], dict):
        warnings_list.append("'layout' should be a dictionary.")
    else:
        # Validate "layout" subfields
        layout = record["layout"]
        
        # Validate "title"
        if "title" not in layout:
            warnings_list.append("Missing 'layout.title' field.")
        # Validate "title.text"
        elif "text" not in layout["title"]:
            warnings_list.append("Missing 'layout.title.text' field.")
        elif not isinstance(layout["title"]["text"], str):
            warnings_list.append("'layout.title.text' should be a string.")
        
        # Validate "xaxis"
        if "xaxis" not in layout:
            warnings_list.append("Missing 'layout.xaxis' field.")
        elif not isinstance(layout["xaxis"], dict):
            warnings_list.append("'layout.xaxis' should be a dictionary.")
        else:
            # Validate "xaxis.title"
            if "title" not in layout["xaxis"]:
                warnings_list.append("Missing 'layout.xaxis.title' field.")
            elif "text" not in layout["xaxis"]["title"]:
                warnings_list.append("Missing 'layout.xaxis.title.text' field.")
            elif not isinstance(layout["xaxis"]["title"]["text"], str):
                warnings_list.append("'layout.xaxis.title.text' should be a string.")
        
        # Validate "yaxis"
        if "yaxis" not in layout:
            warnings_list.append("Missing 'layout.yaxis' field.")
        elif not isinstance(layout["yaxis"], dict):
            warnings_list.append("'layout.yaxis' should be a dictionary.")
        else:
            # Validate "yaxis.title"
            if "title" not in layout["yaxis"]:
                warnings_list.append("Missing 'layout.yaxis.title' field.")
            elif "text" not in layout["yaxis"]["title"]:
                warnings_list.append("Missing 'layout.yaxis.title.text' field.")
            elif not isinstance(layout["yaxis"]["title"]["text"], str):
                warnings_list.append("'layout.yaxis.title.text' should be a string.")
    
    # Return validation result
    if warnings_list:
        print("Warning: There are missing fields in your JSONGrapher record: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2, num_interpolated_points=3, adjust_edges=True):
    """
    Applies a rolling polynomial regression with a specified window size and degree,
    interpolates additional points, and optionally adjusts edge points for smoother transitions.

    Args:
        x_values (list): List of x coordinates.
        y_values (list): List of y coordinates.
        window_size (int): Number of points per rolling fit (default: 3).
        degree (int): Degree of polynomial to fit (default: 2).
        num_interpolated_points (int): Number of interpolated points per segment (default: 3). Set to 0 to only return original points.
        adjust_edges (bool): Whether to adjust edge cases based on window size (default: True).

    Returns:
        tuple: (smoothed_x, smoothed_y) lists for plotting.
    """
    import numpy as np

    smoothed_y = []
    smoothed_x = []

    half_window = window_size // 2  # Number of points to take before & after

    for i in range(len(y_values) - 1):
        # Handle edge cases dynamically based on window size
        left_bound = max(0, i - half_window)
        right_bound = min(len(y_values), i + half_window + 1)

        if adjust_edges:
            if i == 0:  # First point
                right_bound = min(len(y_values), i + window_size)  # Expand to use more points near start
            elif i == len(y_values) - 2:  # Last point
                left_bound = max(0, i - (window_size - 1))  # Expand to include more points near end

        # Select the windowed data
        x_window = np.array(x_values[left_bound:right_bound])
        y_window = np.array(y_values[left_bound:right_bound])

        # Adjust degree based on window size
        adjusted_degree = degree if len(x_window) > 2 else 1  # Use linear fit if only two points are available

        # Fit polynomial & evaluate at current point
        poly_coeffs = np.polyfit(x_window, y_window, deg=adjusted_degree)

        # Generate interpolated points between x_values[i] and x_values[i+1]
        x_interp = np.linspace(x_values[i], x_values[i+1], num_interpolated_points + 2)  # Including endpoints
        y_interp = np.polyval(poly_coeffs, x_interp)

        smoothed_x.extend(x_interp)
        smoothed_y.extend(y_interp)

    return smoothed_x, smoothed_y



## Start of Section of Code for Styles and Converting between plotly and matplotlib Fig objectss ##

'''
#There are a few things to know about the styles logic of JSONGrapher:
(1) There are actually two parts to the plot_style: a layout_style for the graph and a trace_styles_collection which will get applied to the individual dataseries.
   So the plot_style is really supposed to be a dictionary with {"layout_style":"default", "trace_styles_collection":"default"} that way it is JSON compatible and avoids ambiguity. 
   A person can pass in dictionaries for layout_style and for trace_styles_collection and thereby create custom styles.
   There are helper functions to extract style dictionaries once a person has a JSONGrapher record which they're happy with.
(2) We parse what the person provides as a style, so we accept things other than the ideal plot_style dictionary format.  
   If someone provides a single string, we'll use it for both layout_style and trace_styles_collection.
   If we get a list of two, we'll expect that to be in the order of layout_style then trace_styles_collection
   If we get a string that we can't find in the existing styles list, then we'll use the default. 
(1) by default, export to json will *not* include plot_styles.  include_formatting will be an optional argument. 
(2) There is an apply_plot_style function which will first put the style into self.fig_dict['plot_style'] so it stays there, before applying the style.
(3) For the plotting functions, they will have plot_style = {"layout_style":"", "trace_styles_collection":""} or = '' as their default argument value, which will result in checking if plot_style exists in the self.fig_dict already. If so, it will be used. 
    If somebody passes in a "None" type or the word none, then *no* style changes will be applied during plotting, relative to what the record already has.
    One can pass a style in for the plotting functions. In those cases, we'll use the remove style option, then apply.
'''

def parse_plot_style(plot_style):
    """
    Parse the given plot style and return a structured dictionary for layout and data series styles.
    If plot_style is missing a layout_style or trace_styles_collection then will set them as an empty string.
    
    :param plot_style: None, str, list of two items, or a dictionary with at least one valid field.
    :return: dict with "layout_style" and "trace_styles_collection", ensuring defaults if missing.
    """
    if plot_style is None:
        parsed_plot_style = {"layout_style": None, "trace_styles_collection": None}
    elif isinstance(plot_style, str):
        parsed_plot_style = {"layout_style": plot_style, "trace_styles_collection": plot_style}
    elif isinstance(plot_style, list) and len(plot_style) == 2:
        parsed_plot_style = {"layout_style": plot_style[0], "trace_styles_collection": plot_style[1]}
    elif isinstance(plot_style, dict):
        if "trace_styles_collection" not in plot_style:
            if "trace_style_collection" in plot_style:
                print("Warning: plot_style has 'trace_style_collection', this key should be 'trace_styles_collection'.  The key is being used, but the spelling error should be fixed.")
                plot_style["traces_styles_collection"] = plot_style["trace_style_collection"]
            elif "traces_style_collection" in plot_style:
                print("Warning: plot_style has 'traces_style_collection', this key should be 'trace_styles_collection'.  The key is being used, but the spelling error should be fixed.")
                plot_style["traces_styles_collection"] = plot_style["traces_style_collection"]
            else:
                plot_style.setdefault("trace_styles_collection", '')
        if "layout_style" not in plot_style: 
            plot_style.setdefault("layout_style", '')
        parsed_plot_style = {
            "layout_style": plot_style.get("layout_style", None),
            "trace_styles_collection": plot_style.get("trace_styles_collection", None),
        }
    else:
        raise ValueError("Invalid plot style: Must be None, a string, a list of two items, or a dictionary with valid fields.")
    return parsed_plot_style

#this function uses a stylename or list of stylename/dictionaries to apply *both* layout_style and trace_styles_collection
#plot_style is a dictionary of form {"layout_style":"default", "trace_styles_collection":"default"}
#However, the style_to_apply does not need to be passed in as a dictionary.
#For example: style_to_apply = ['default', 'default'] or style_to_apply = 'science'.
#IMPORTANT: This is the only function that will set a layout_style or trace_styles_collection that is an empty string into 'default'.
# all other style applying functions (including parse_plot_style) will pass on the empty string or will do nothing if receiving an empty string.
def apply_plot_style_to_plotly_dict(fig_dict, plot_style = {"layout_style":"", "trace_styles_collection":""}):
    #We first parse style_to_apply to get a properly formatted plot_style dictionary of form: {"layout_style":"default", "trace_styles_collection":"default"}
    plot_style = parse_plot_style(plot_style)
    plot_style.setdefault("layout_style",'') #fill with blank string if not present.
    plot_style.setdefault("trace_styles_collection",'')  #fill with blank string if not present.
    #Code logic for layout style.
    if str(plot_style["layout_style"]).lower() != 'none': #take no action if received "None" or NoneType
        if plot_style["layout_style"] == '': #in this case, we're going to use the default.
            plot_style["layout_style"] = 'default'
        fig_dict = remove_layout_style_from_plotly_dict(fig_dict=fig_dict)
        fig_dict = apply_layout_style_to_plotly_dict(fig_dict=fig_dict, layout_style_to_apply=plot_style["layout_style"])
    #Code logic for trace_styles_collection style.
    if str(plot_style["trace_styles_collection"]).lower() != 'none': #take no action if received "None" or NoneType
        if plot_style["trace_styles_collection"] == '': #in this case, we're going to use the default.
            plot_style["trace_styles_collection"] = 'default'            
        fig_dict = remove_trace_styles_collection_from_plotly_dict(fig_dict=fig_dict)
        fig_dict = apply_trace_styles_collection_to_plotly_dict(fig_dict=fig_dict,trace_styles_collection=plot_style["trace_styles_collection"])
    return fig_dict

def remove_plot_style_from_plotly_dict(fig_dict):
    """
    Remove both layout and data series styles from a Plotly figure dictionary.

    :param fig_dict: dict, Plotly style fig_dict
    :return: dict, Updated Plotly style fig_dict with default formatting.
    """
    fig_dict = remove_layout_style_from_plotly_dict(fig_dict)
    fig_dict = remove_trace_styles_collection_from_plotly_dict(fig_dict)
    return fig_dict


def convert_JSONGrapher_dict_to_matplotlib_fig(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure without using pio.from_json.

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The corresponding Matplotlib figure.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    # Extract traces (data series)
    #This section is now deprecated. It has not been completely updated after the trace_style field was created.
    #There was old logic for trace_type which has been partially updated, but in fact the logic should be rewritten
    #to better accommodate the existence of both "trace_style" and "type". It may be that there should be
    #a helper function called 
    for trace in fig_dict.get("data", []):
        trace_style = trace.get("trace_style", '')
        trace_type = trace.get("type", '')
        if (trace_type == '') and (trace_style == ''):
            trace_style = 'scatter_spline'
        elif (trace_type == 'scatter') and (trace_style == ''):
            trace_style = 'scatter_spline'
        elif (trace_style == '') and (trace_type != ''):
            trace_style = trace_type
        # If type is missing, but mode indicates lines and shape is spline, assume it's a spline
        if not trace_style and trace.get("mode") == "lines" and trace.get("line", {}).get("shape") == "spline":
            trace_style = "spline"
        x_values = trace.get("x", [])
        y_values = trace.get("y", [])
        trace_name = trace.get("name", "Data")
        if trace_style == "bar":
            ax.bar(x_values, y_values, label=trace_name)
        elif trace_style == "scatter":
            mode = trace.get("mode", "")
            ax.scatter(x_values, y_values, label=trace_name, alpha=0.7)
        elif trace_style == "scatter_spline":
            mode = trace.get("mode", "")
            ax.scatter(x_values, y_values, label=trace_name, alpha=0.7)
            # Attempt to simulate spline behavior if requested
            if "lines" in mode or trace.get("line", {}).get("shape") == "spline":
                print("Warning: Rolling polynomial approximation used instead of spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
                print("line 1530", x_smooth, y_smooth, x_values, y_values)
                # Add a label explicitly for the legend
                ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")
        elif trace_style == "spline":
            print("Warning: Using rolling polynomial approximation instead of true spline.")
            x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
            print("line 1536", x_smooth, y_smooth, x_values, y_values)
            ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")

    # Extract layout details
    layout = fig_dict.get("layout", {})
    title = layout.get("title", {})
    if isinstance(title, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        ax.set_title(title.get("text", "Converted Plotly Figure"))
    else:
        ax.set_title(title if isinstance(title, str) else "Converted Plotly Figure")

    xaxis = layout.get("xaxis", {})
    xlabel = "X-Axis"  # Default label
    if isinstance(xaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = xaxis.get("title", {})
        xlabel = title_obj.get("text", "X-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(xaxis, str):
        xlabel = xaxis  # If it's a string, use it directly
    ax.set_xlabel(xlabel)
    yaxis = layout.get("yaxis", {})
    ylabel = "Y-Axis"  # Default label
    if isinstance(yaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = yaxis.get("title", {})
        ylabel = title_obj.get("text", "Y-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(yaxis, str):
        ylabel = yaxis  # If it's a string, use it directly
    ax.set_ylabel(ylabel)
    ax.legend()
    return fig
    

#The below function works, but because it depends on the python plotly package, we avoid using it
#To decrease the number of dependencies. 
def convert_plotly_dict_to_matplotlib(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure.

    Supports: Bar Charts, Scatter Plots, Spline curves using rolling polynomial regression.

    This functiony has a dependency on the plotly python package (pip install plotly)

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The corresponding Matplotlib figure.
    """
    import plotly.io as pio
    import matplotlib.pyplot as plt
    # Convert JSON dictionary into a Plotly figure
    plotly_fig = pio.from_json(json.dumps(fig_dict))

    # Create a Matplotlib figure
    fig, ax = plt.subplots()

    for trace in plotly_fig.data:
        if trace.type == "bar":
            ax.bar(trace.x, trace.y, label=trace.name if trace.name else "Bar Data")

        elif trace.type == "scatter":
            mode = trace.mode if isinstance(trace.mode, str) else ""
            line_shape = trace.line["shape"] if hasattr(trace, "line") and "shape" in trace.line else None

            # Plot raw scatter points
            ax.scatter(trace.x, trace.y, label=trace.name if trace.name else "Scatter Data", alpha=0.7)

            # If spline is requested, apply rolling polynomial smoothing
            if line_shape == "spline" or "lines" in mode:
                print("Warning: During the matploglib conversion, a rolling polynomial will be used instead of a spline, whereas JSONGrapher uses a true spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(trace.x, trace.y, window_size=3, degree=2)
                ax.plot(x_smooth, y_smooth, linestyle="-", label=trace.name + " Spline" if trace.name else "Spline Curve")

    ax.legend()
    ax.set_title(plotly_fig.layout.title.text if plotly_fig.layout.title else "Converted Plotly Figure")
    ax.set_xlabel(plotly_fig.layout.xaxis.title.text if plotly_fig.layout.xaxis.title else "X-Axis")
    ax.set_ylabel(plotly_fig.layout.yaxis.title.text if plotly_fig.layout.yaxis.title else "Y-Axis")

    return fig

def apply_trace_styles_collection_to_plotly_dict(fig_dict, trace_styles_collection="default", trace_style_to_apply="default"):
    """
    Iterates over all traces in the `data` list of a Plotly figure dictionary 
    and applies styles to each one.

    Args:
        fig_dict (dict): A dictionary containing a `data` field with Plotly traces.
        trace_style_to_apply (str): Optional style preset to apply. Default is "default".

    Returns:
        dict: Updated Plotly figure dictionary with defaults applied to each trace.

    """
    if type(trace_styles_collection) == type("string"):
        trace_styles_collection_name = trace_styles_collection
    else:
        trace_styles_collection_name = trace_styles_collection["name"]

    if "data" in fig_dict and isinstance(fig_dict["data"], list):
        fig_dict["data"] = [apply_trace_style_to_single_data_series(data_series=trace,trace_styles_collection=trace_styles_collection, trace_style_to_apply=trace_style_to_apply) for trace in fig_dict["data"]]
    #now note
    if "plot_style" not in fig_dict:
        fig_dict["plot_style"] = {}
    fig_dict["plot_style"]["trace_styles_collection"] = trace_styles_collection_name
    return fig_dict


# The logic in JSONGrapher is to apply the style information but to treat "type" differently 
# Accordingly, we use 'trace_styles_collection' as a field in JSONGrapher for each data_series.
# compared to how plotly treats 'type' for a data series. So later in the process, when actually plotting with plotly, the 'type' field will get overwritten.
def apply_trace_style_to_single_data_series(data_series, trace_styles_collection="default", trace_style_to_apply="default"):
    """
    Applies predefined styles to a single Plotly data series while preserving relevant fields.

    Args:
        data_series (dict): A dictionary representing a single Plotly data series.
        trace_style_to_apply (str or dict): Name of the style preset or a custom style dictionary. Default is "default".

    Returns:
        dict: Updated data series with style applied.
    """
    if (trace_styles_collection == '') or (str(trace_styles_collection).lower() == 'none'):
        return data_series    
    if not isinstance(data_series, dict):
        return data_series  # Return unchanged if the data series is invalid.
    if type(trace_style_to_apply) == type("string"):
        if (trace_style_to_apply.lower() == "nature") or (trace_style_to_apply.lower() == "science"):
            trace_style_to_apply = "default"
    # -------------------------------
    # Predefined data series styles
    # -------------------------------
    # Each style is defined as a dictionary containing multiple plot types.
    # Users can select a style preset (e.g., "default", "minimalist", "bold"),
    # and the function will apply appropriate settings for the given plot type.
    #
    # Supported plot types:
    # - "scatter_spline" (default when type is not specified)
    # - "scatter"
    # - "spline"
    # - "bar"
    # - "heatmap"
    #
    # Note: Colors are intentionally omitted to allow users to define their own.
    # However, predefined colorscales are applied for heatmaps.
    
    styles_available = {
        "default": {
            "scatter_spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 10},
            },
            "scatter_line": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "linear", "width": 2},
                "marker": {"size": 10},
            },
            "scatter": {
                "type": "scatter",
                "mode": "markers",
                "marker": {"size": 10},
            },
            "spline": {
                "type": "scatter",
                "mode": "lines",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 0},  # Hide markers for smooth curves
            },
            "bar": {
                "type": "bar",
                "marker": {
                                "color": "blue",
                                "opacity": 0.8,
                                "line": {
                                    "color": "black",
                                    "width": 2
                                }
                            },
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Viridis",
            }
        },
        "minimalist": {
            "scatter_spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 1},
                "marker": {"size": 6},
            },
            "scatter": {
                "type": "scatter",
                "mode": "lines",
                "line": {"shape": "linear", "width": 1},
                "marker": {"size": 0},
            },
            "spline": {
                "type": "scatter",
                "mode": "lines",
                "line": {"shape": "spline", "width": 1},
                "marker": {"size": 0},
            },
            "bar": {
                "type": "bar",
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Greys",
            }
        },
        "bold": {
            "scatter_spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 4},
                "marker": {"size": 10},
            },
            "scatter": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 4},
                "marker": {"size": 12},
            },
            "spline": {
                "type": "scatter",
                "mode": "lines",
                "line": {"shape": "spline", "width": 4},
                "marker": {"size": 0},
            },
            "bar": {
                "type": "bar",
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Jet",
            }
        },
                "scatter": { #this style forces all traces into scatter.
            "scatter_spline": {
                "type": "scatter",
                "mode": "markers",
                "marker": {"size": 10},
            },
            "scatter": {
                "type": "scatter",
                "mode": "markers",
                "marker": {"size": 10},
            },
            "spline": {
                "type": "scatter",
                "mode": "markers",
                "marker": {"size": 10},
            },
            "bar": {
                "type": "scatter",
                "mode": "markers",
                "marker": {"size": 10},
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Viridis",
            }
        },
        "scatter_spline": { #this style forces all traces into scatter_spline
            "scatter_spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 10},
            },
            "scatter": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 10},
            },
            "spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 10},
            },
            "bar": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 10},
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Viridis",
            }
        },
        "scatter_spline": { #this style forces all traces into spline only
            "scatter_spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 0},
            },
            "scatter": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 0},
            },
            "spline": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 0},
            },
            "bar": {
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"shape": "spline", "width": 2},
                "marker": {"size": 0},
            },
            "heatmap": {
                "type": "heatmap",
                "colorscale": "Viridis",
            }
        }
    }
    # Get the appropriate style dictionary
    if isinstance(trace_styles_collection, dict):
        styles_collection_dict = trace_styles_collection  # Use custom style directly
    else:
        styles_collection_dict = styles_available.get(trace_styles_collection, {})
        if not styles_collection_dict:  # Check if it's an empty dictionary
            print(f"Warning: Style named '{trace_styles_collection}' not found for individual data series. Using 'default' trace_styles_collection instead.")
            styles_collection_dict = styles_available.get("default", {})
    # Determine the trace_style, defaulting to the first item in a given style if none is provided.
    trace_style = data_series.get("trace_style", "")
    if trace_style == "":
        trace_style = list(styles_collection_dict.keys())[0] #take the first trace_style name in the style_dict.  In python 3.7 and later dictionary keys preserve ordering.
    
    # Retrieve the specific style for the plot type
    trace_style = styles_collection_dict.get(trace_style, {})
    # Apply type and other predefined settings
    data_series["type"] = trace_style.get("type", data_series.get("type", trace_style))
    # Apply other attributes while preserving existing values
    for key, value in trace_style.items():
        if key not in ["type"]:
            if isinstance(value, dict):  # Ensure value is a dictionary
                data_series.setdefault(key, {}).update(value)
            else:
                data_series[key] = value  # Direct assignment for non-dictionary values
    return data_series

def remove_trace_styles_collection_from_plotly_dict(fig_dict):
    """
    Remove applied data series styles from a Plotly figure dictionary.
    
    :param fig_dict: dict, Plotly style fig_dict
    :return: dict, Updated Plotly style fig_dict with default formatting.
    """
    if isinstance(fig_dict, dict) and "data" in fig_dict and isinstance(fig_dict["data"], list):
        fig_dict["data"] = [remove_trace_style_from_single_data_series(trace) for trace in fig_dict["data"]]

    #If being told to remove the style, should also pop it from fig_dict.
    if "plot_style" in fig_dict:
        if "trace_styles_collection" in fig_dict["plot_style"]:
            fig_dict["plot_style"].pop("trace_styles_collection")
    return fig_dict

def remove_trace_style_from_single_data_series(data_series):
    """
    Remove only formatting fields from a single Plotly data series while preserving all other fields.

    Note: Since fig_dict data objects may contain custom fields (e.g., "equation", "metadata"),
    this function explicitly removes predefined **formatting** attributes while leaving all other data intact.

    :param data_series: dict, A dictionary representing a single Plotly data series.
    :return: dict, Updated data series with formatting fields removed but key data retained.
    """

    if not isinstance(data_series, dict):
        return data_series  # Return unchanged if input is invalid.

    # **Define formatting fields to remove**
    formatting_fields = {
        "mode", "line", "marker", "colorscale", "opacity", "fill", "fillcolor",
        "legendgroup", "showlegend", "textposition", "textfont"
    }

    # **Create a new data series excluding only formatting fields**
    cleaned_data_series = {key: value for key, value in data_series.items() if key not in formatting_fields}

    return cleaned_data_series

def extract_trace_style_by_index(fig_dict, data_series_index, new_trace_style_name=''):
    data_series_dict = fig_dict["data"][data_series_index]
    extracted_trace_style = extract_trace_style_from_data_series_dict(data_series_dict=data_series_dict, new_trace_style_name=new_trace_style_name)
    return extracted_trace_style


def extract_trace_style_from_data_series_dict(data_series_dict, new_trace_style_name=''):
    """
    Extract formatting attributes from a given Plotly data series.

    The function scans the provided `data_series` dictionary and returns a new dictionary
    containing only the predefined formatting fields.

    Examples of formatting attributes extracted:
    - "type"
    - "mode"
    - "line"
    - "marker"
    - "colorscale"
    - "opacity"
    - "fill"
    - "fillcolor"
    - "legendgroup"
    - "showlegend"
    - "textposition"
    - "textfont"

    :param data_series_dict: dict, A dictionary representing a single Plotly data series.
    :param trace_style: string, the key name for what user wants to call the trace_style in the style, after extraction.
    :return: dict, A dictionary containing only the formatting attributes.
    """

    if new_trace_style_name=='':
        data_series_dict.get("trace_style", "") #keep blank if not present.
    if new_trace_style_name=='':
        new_trace_style_name = "custom"

    if not isinstance(data_series_dict, dict):
        return {}  # Return an empty dictionary if input is invalid.

    # Define known formatting attributes
    formatting_fields = {
        "type", "mode", "line", "marker", "colorscale", "opacity", "fill", "fillcolor",
        "legendgroup", "showlegend", "textposition", "textfont"
    }

    # Extract only formatting-related attributes
    trace_style_dict = {key: value for key, value in data_series_dict.items() if key in formatting_fields}
    extracted_trace_style = {new_trace_style_name : trace_style_dict} #this is a trace_style dict.
    return extracted_trace_style #this is a trace_style dict.

#export a single trace_style dictionary to .json.
def export_trace_style(trace_style_dict, trace_style_name, filename):
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    json_structure = {
        "trace_style": {
            "name": trace_style_name,
            trace_style_name: {
                trace_style_dict
            }
        }
    }

    with open(filename, "w") as file:
        json.dump(json_structure, file, indent=4)

#export an entire trace_styles_collection to .json. THe trace_styles_collection is dict.
def export_trace_styles_collection(trace_styles_collection, trace_styles_collection_name, filename):
    if "trace_styles_collection" in trace_styles_collection: #We may receive a traces_style collection in a container. If so, we pull the traces_style_collection out.
        trace_styles_collection = trace_styles_collection[trace_styles_collection["name"]] 
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    json_structure = {
        "trace_styles_collection": {
            "name": trace_styles_collection_name,
            trace_styles_collection_name: trace_styles_collection
        }
    }
    print("line 1964", json_structure)
    with open(filename, "w") as file:
        json.dump(json_structure, file, indent=4)

#export an entire trace_styles_collection from .json. THe trace_styles_collection is dict.
def import_trace_styles_collection(filename):
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    with open(filename, "r") as file:
        data = json.load(file)

    # Validate JSON structure
    containing_dict = data.get("trace_styles_collection")
    if not isinstance(containing_dict, dict):
        raise ValueError("Error: Missing or malformed 'trace_styles_collection'.")

    collection_name = containing_dict.get("name")
    if not isinstance(collection_name, str) or collection_name not in containing_dict:
        raise ValueError(f"Error: Expected dictionary '{collection_name}' is missing or malformed.")
    trace_styles_collection  = containing_dict[collection_name]
    # Return only the dictionary corresponding to the collection name
    return trace_styles_collection


#export an entire trace_styles_collection from .json. THe trace_styles_collection is dict.
def import_trace_style(filename):
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    with open(filename, "r") as file:
        data = json.load(file)

    # Validate JSON structure
    containing_dict = data.get("trace_style")
    if not isinstance(containing_dict, dict):
        raise ValueError("Error: Missing or malformed 'trace_style'.")

    style_name = containing_dict.get("name")
    if not isinstance(style_name, str) or style_name not in containing_dict:
        raise ValueError(f"Error: Expected dictionary '{style_name}' is missing or malformed.")
    trace_style_dict = containing_dict[style_name]

    # Return only the dictionary corresponding to the trace style name
    return trace_style_dict


def apply_layout_style_to_plotly_dict(fig_dict, layout_style_to_apply="default"):
    """
    Apply a predefined style to a Plotly fig_dict while preserving non-cosmetic fields.
    
    :param fig_dict: dict, Plotly style fig_dict
    :param layout_style_to_apply: str, Name of the style or journal, or a style dictionary to apply.
    :return: dict, Updated Plotly style fig_dict.
    """
    if type(layout_style_to_apply) == type("string"):
        layout_style_to_apply_name = layout_style_to_apply
    else:
        layout_style_to_apply_name = list(layout_style_to_apply.keys())[0]#if it is a dictionary, it will have one key which is its name.
    if (layout_style_to_apply == '') or (str(layout_style_to_apply).lower() == 'none'):
        return fig_dict

    #Hardcoding some cases as ones that will call the default layout, for convenience.
    if (layout_style_to_apply.lower() == "minimalist") or (layout_style_to_apply.lower() == "bold"):
        layout_style_to_apply = "default"

    styles_available = {
        "default": {
            "layout": {
                "title": {"font": {"size": 32}, "x": 0.5},
                "xaxis": {"title": {"font": {"size": 27}}, "tickfont": {"size": 23}},
                "yaxis": {"title": {"font": {"size": 27}}, "tickfont": {"size": 23}},
                "legend": {
                    "title": {"font": {"size": 22}},
                    "font": {"size": 22}
                }
            }
        },
        "Nature": {
            "layout": {
                "title": {"font": {"size": 32, "family": "Times New Roman", "color": "black"}},
                "font": {"size": 25, "family": "Times New Roman"},
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
                "xaxis": {
                    "showgrid": True, "gridcolor": "#ddd", "gridwidth": 1,
                    "linecolor": "black", "linewidth": 2, "ticks": "outside",
                    "tickwidth": 2, "tickcolor": "black"
                },
                "yaxis": {
                    "showgrid": True, "gridcolor": "#ddd", "gridwidth": 1,
                    "linecolor": "black", "linewidth": 2, "ticks": "outside",
                    "tickwidth": 2, "tickcolor": "black"
                }
            }
        },
        "Science": {
            "layout": {
                "title": {"font": {"size": 32, "family": "Arial", "color": "black"}},
                "font": {"size": 25, "family": "Arial"},
                "paper_bgcolor": "white",
                "plot_bgcolor": "white",
                "xaxis": {
                    "showgrid": True, "gridcolor": "#ccc", "gridwidth": 1,
                    "linecolor": "black", "linewidth": 2, "ticks": "outside",
                    "tickwidth": 2, "tickcolor": "black"
                },
                "yaxis": {
                    "showgrid": True, "gridcolor": "#ccc", "gridwidth": 1,
                    "linecolor": "black", "linewidth": 2, "ticks": "outside",
                    "tickwidth": 2, "tickcolor": "black"
                }
            }
        }
    }

    # Use or get the style specified, or use default if not found
    if isinstance(layout_style_to_apply, dict):
        style_dict = layout_style_to_apply
    else:
        style_dict = styles_available.get(layout_style_to_apply, {})
        if not style_dict:  # Check if it's an empty dictionary
            print(f"Style named '{layout_style_to_apply}' not found with explicit layout dictionary. Using 'default' layout style.")
            style_dict = styles_available.get("default", {})

    # Ensure layout exists in the figure
    fig_dict.setdefault("layout", {})

    # **Extract non-cosmetic fields**
    non_cosmetic_fields = {
        "title.text": fig_dict.get("layout", {}).get("title", {}).get("text", None),
        "xaxis.title.text": fig_dict.get("layout", {}).get("xaxis", {}).get("title", {}).get("text", None),
        "yaxis.title.text": fig_dict.get("layout", {}).get("yaxis", {}).get("title", {}).get("text", None),
        "legend.title.text": fig_dict.get("layout", {}).get("legend", {}).get("title", {}).get("text", None),
        "annotations.text": [
            annotation.get("text", None) for annotation in fig_dict.get("layout", {}).get("annotations", [])
        ],
        "updatemenus.buttons.label": [
            button.get("label", None) for menu in fig_dict.get("layout", {}).get("updatemenus", [])
            for button in menu.get("buttons", [])
        ],
        "coloraxis.colorbar.title.text": fig_dict.get("layout", {}).get("coloraxis", {}).get("colorbar", {}).get("title", {}).get("text", None),
    }

    # **Apply style dictionary to create a fresh layout object**
    new_layout = style_dict.get("layout", {}).copy()

    # **Restore non-cosmetic fields**
    if non_cosmetic_fields["title.text"]:
        new_layout.setdefault("title", {})["text"] = non_cosmetic_fields["title.text"]

    if non_cosmetic_fields["xaxis.title.text"]:
        new_layout.setdefault("xaxis", {}).setdefault("title", {})["text"] = non_cosmetic_fields["xaxis.title.text"]

    if non_cosmetic_fields["yaxis.title.text"]:
        new_layout.setdefault("yaxis", {}).setdefault("title", {})["text"] = non_cosmetic_fields["yaxis.title.text"]

    if non_cosmetic_fields["legend.title.text"]:
        new_layout.setdefault("legend", {}).setdefault("title", {})["text"] = non_cosmetic_fields["legend.title.text"]

    if non_cosmetic_fields["annotations.text"]:
        new_layout["annotations"] = [{"text": text} for text in non_cosmetic_fields["annotations.text"]]

    if non_cosmetic_fields["updatemenus.buttons.label"]:
        new_layout["updatemenus"] = [{"buttons": [{"label": label} for label in non_cosmetic_fields["updatemenus.buttons.label"]]}]

    if non_cosmetic_fields["coloraxis.colorbar.title.text"]:
        new_layout.setdefault("coloraxis", {}).setdefault("colorbar", {})["title"] = {"text": non_cosmetic_fields["coloraxis.colorbar.title.text"]}

    # **Assign the new layout back into the figure dictionary**
    fig_dict["layout"] = new_layout
    #Now update the fig_dict to signify the new layout_style used.
    if "plot_style" not in fig_dict:
        fig_dict["plot_style"] = {}
    fig_dict["plot_style"]["layout_style"] = layout_style_to_apply_name
    return fig_dict

def remove_layout_style_from_plotly_dict(fig_dict):
    """
    Remove applied layout styles from a Plotly figure dictionary while preserving essential content.

    :param fig_dict: dict, Plotly style fig_dict
    :return: dict, Updated Plotly style fig_dict with styles removed but key data intact.
    """
    if "layout" in fig_dict:
        style_keys = ["font", "paper_bgcolor", "plot_bgcolor", "gridcolor", "gridwidth", "tickfont", "linewidth"]

        # **Store non-cosmetic fields if present, otherwise assign None**
        non_cosmetic_fields = {
            "title.text": fig_dict.get("layout", {}).get("title", {}).get("text", None),
            "xaxis.title.text": fig_dict.get("layout", {}).get("xaxis", {}).get("title", {}).get("text", None),
            "yaxis.title.text": fig_dict.get("layout", {}).get("yaxis", {}).get("title", {}).get("text", None),
            "legend.title.text": fig_dict.get("layout", {}).get("legend", {}).get("title", {}).get("text", None),
            "annotations.text": [annotation.get("text", None) for annotation in fig_dict.get("layout", {}).get("annotations", [])],
            "updatemenus.buttons.label": [
                button.get("label", None) for menu in fig_dict.get("layout", {}).get("updatemenus", [])
                for button in menu.get("buttons", [])
            ],
            "coloraxis.colorbar.title.text": fig_dict.get("layout", {}).get("coloraxis", {}).get("colorbar", {}).get("title", {}).get("text", None),
        }

        # Preserve title text while removing font styling
        if "title" in fig_dict["layout"] and isinstance(fig_dict["layout"]["title"], dict):
            fig_dict["layout"]["title"] = {"text": non_cosmetic_fields["title.text"]} if non_cosmetic_fields["title.text"] is not None else {}

        # Preserve axis titles while stripping font styles
        for axis in ["xaxis", "yaxis"]:
            if axis in fig_dict["layout"] and isinstance(fig_dict["layout"][axis], dict):
                if "title" in fig_dict["layout"][axis] and isinstance(fig_dict["layout"][axis]["title"], dict):
                    fig_dict["layout"][axis]["title"] = {"text": non_cosmetic_fields[f"{axis}.title.text"]} if non_cosmetic_fields[f"{axis}.title.text"] is not None else {}

                # Remove style-related attributes but keep axis configurations
                for key in style_keys:
                    fig_dict["layout"][axis].pop(key, None)

        # Preserve legend title text while stripping font styling
        if "legend" in fig_dict["layout"] and isinstance(fig_dict["layout"]["legend"], dict):
            if "title" in fig_dict["layout"]["legend"] and isinstance(fig_dict["layout"]["legend"]["title"], dict):
                fig_dict["layout"]["legend"]["title"] = {"text": non_cosmetic_fields["legend.title.text"]} if non_cosmetic_fields["legend.title.text"] is not None else {}
            fig_dict["layout"]["legend"].pop("font", None)

        # Preserve annotations text while stripping style attributes
        if "annotations" in fig_dict["layout"]:
            fig_dict["layout"]["annotations"] = [
                {"text": text} if text is not None else {} for text in non_cosmetic_fields["annotations.text"]
            ]

        # Preserve update menu labels while stripping styles
        if "updatemenus" in fig_dict["layout"]:
            for menu in fig_dict["layout"]["updatemenus"]:
                for i, button in enumerate(menu.get("buttons", [])):
                    button.clear()
                    if non_cosmetic_fields["updatemenus.buttons.label"][i] is not None:
                        button["label"] = non_cosmetic_fields["updatemenus.buttons.label"][i]

        # Preserve color bar title while stripping styles
        if "coloraxis" in fig_dict["layout"] and "colorbar" in fig_dict["layout"]["coloraxis"]:
            fig_dict["layout"]["coloraxis"]["colorbar"]["title"] = {"text": non_cosmetic_fields["coloraxis.colorbar.title.text"]} if non_cosmetic_fields["coloraxis.colorbar.title.text"] is not None else {}

        # Remove general style settings without clearing layout structure
        for key in style_keys:
            fig_dict["layout"].pop(key, None)

    #If being told to remove the style, should also pop it from fig_dict.
    if "plot_style" in fig_dict:
        if "layout_style" in fig_dict["plot_style"]:
            fig_dict["plot_style"].pop("layout_style")
    return fig_dict

def extract_layout_style_from_plotly_dict(fig_dict):
    """
    Extract a layout style dictionary from a given Plotly JSON object, including background color, grids, and other appearance attributes.

    :param fig_dict: dict, Plotly JSON object.
    :return: dict, Extracted style settings.
    """


    # **Extraction Phase** - Collect cosmetic fields if they exist
    layout = fig_dict.get("layout", {})

    # Note: Each assignment below will return None if the corresponding field is missing
    title_font = layout.get("title", {}).get("font")
    title_x = layout.get("title", {}).get("x")
    title_y = layout.get("title", {}).get("y")

    global_font = layout.get("font")
    paper_bgcolor = layout.get("paper_bgcolor")
    plot_bgcolor = layout.get("plot_bgcolor")
    margin = layout.get("margin")

    # Extract x-axis cosmetic fields
    xaxis_title_font = layout.get("xaxis", {}).get("title", {}).get("font")
    xaxis_tickfont = layout.get("xaxis", {}).get("tickfont")
    xaxis_gridcolor = layout.get("xaxis", {}).get("gridcolor")
    xaxis_gridwidth = layout.get("xaxis", {}).get("gridwidth")
    xaxis_zerolinecolor = layout.get("xaxis", {}).get("zerolinecolor")
    xaxis_zerolinewidth = layout.get("xaxis", {}).get("zerolinewidth")
    xaxis_tickangle = layout.get("xaxis", {}).get("tickangle")

    # **Set flag for x-axis extraction**
    xaxis = any([
        xaxis_title_font, xaxis_tickfont, xaxis_gridcolor, xaxis_gridwidth,
        xaxis_zerolinecolor, xaxis_zerolinewidth, xaxis_tickangle
    ])

    # Extract y-axis cosmetic fields
    yaxis_title_font = layout.get("yaxis", {}).get("title", {}).get("font")
    yaxis_tickfont = layout.get("yaxis", {}).get("tickfont")
    yaxis_gridcolor = layout.get("yaxis", {}).get("gridcolor")
    yaxis_gridwidth = layout.get("yaxis", {}).get("gridwidth")
    yaxis_zerolinecolor = layout.get("yaxis", {}).get("zerolinecolor")
    yaxis_zerolinewidth = layout.get("yaxis", {}).get("zerolinewidth")
    yaxis_tickangle = layout.get("yaxis", {}).get("tickangle")

    # **Set flag for y-axis extraction**
    yaxis = any([
        yaxis_title_font, yaxis_tickfont, yaxis_gridcolor, yaxis_gridwidth,
        yaxis_zerolinecolor, yaxis_zerolinewidth, yaxis_tickangle
    ])

    # Extract legend styling
    legend_font = layout.get("legend", {}).get("font")
    legend_x = layout.get("legend", {}).get("x")
    legend_y = layout.get("legend", {}).get("y")

    # **Assignment Phase** - Reconstruct dictionary in a structured manner
    extracted_layout_style = {"layout": {}}

    if title_font or title_x:
        extracted_layout_style["layout"]["title"] = {}
        if title_font:
            extracted_layout_style["layout"]["title"]["font"] = title_font
        if title_x:
            extracted_layout_style["layout"]["title"]["x"] = title_x
        if title_y:
            extracted_layout_style["layout"]["title"]["y"] = title_y

    if global_font:
        extracted_layout_style["layout"]["font"] = global_font

    if paper_bgcolor:
        extracted_layout_style["layout"]["paper_bgcolor"] = paper_bgcolor
    if plot_bgcolor:
        extracted_layout_style["layout"]["plot_bgcolor"] = plot_bgcolor
    if margin:
        extracted_layout_style["layout"]["margin"] = margin

    if xaxis:
        extracted_layout_style["layout"]["xaxis"] = {}
        if xaxis_title_font:
            extracted_layout_style["layout"]["xaxis"]["title"] = {"font": xaxis_title_font}
        if xaxis_tickfont:
            extracted_layout_style["layout"]["xaxis"]["tickfont"] = xaxis_tickfont
        if xaxis_gridcolor:
            extracted_layout_style["layout"]["xaxis"]["gridcolor"] = xaxis_gridcolor
        if xaxis_gridwidth:
            extracted_layout_style["layout"]["xaxis"]["gridwidth"] = xaxis_gridwidth
        if xaxis_zerolinecolor:
            extracted_layout_style["layout"]["xaxis"]["zerolinecolor"] = xaxis_zerolinecolor
        if xaxis_zerolinewidth:
            extracted_layout_style["layout"]["xaxis"]["zerolinewidth"] = xaxis_zerolinewidth
        if xaxis_tickangle:
            extracted_layout_style["layout"]["xaxis"]["tickangle"] = xaxis_tickangle

    if yaxis:
        extracted_layout_style["layout"]["yaxis"] = {}
        if yaxis_title_font:
            extracted_layout_style["layout"]["yaxis"]["title"] = {"font": yaxis_title_font}
        if yaxis_tickfont:
            extracted_layout_style["layout"]["yaxis"]["tickfont"] = yaxis_tickfont
        if yaxis_gridcolor:
            extracted_layout_style["layout"]["yaxis"]["gridcolor"] = yaxis_gridcolor
        if yaxis_gridwidth:
            extracted_layout_style["layout"]["yaxis"]["gridwidth"] = yaxis_gridwidth
        if yaxis_zerolinecolor:
            extracted_layout_style["layout"]["yaxis"]["zerolinecolor"] = yaxis_zerolinecolor
        if yaxis_zerolinewidth:
            extracted_layout_style["layout"]["yaxis"]["zerolinewidth"] = yaxis_zerolinewidth
        if yaxis_tickangle:
            extracted_layout_style["layout"]["yaxis"]["tickangle"] = yaxis_tickangle

    if legend_font or legend_x or legend_y:
        extracted_layout_style["layout"]["legend"] = {}
        if legend_font:
            extracted_layout_style["layout"]["legend"]["font"] = legend_font
        if legend_x:
            extracted_layout_style["layout"]["legend"]["x"] = legend_x
        if legend_y:
            extracted_layout_style["layout"]["legend"]["y"] = legend_y

    return extracted_layout_style

## Start of Section of Code for Styles and Converting between plotly and matplotlib Fig objectss ##

### Start of section of code with functions for extracting and updating x and y ranges of data series ###

def update_implicit_data_series_x_ranges(fig_dict, range_dict):
    """
    Updates the x_range_default values for all simulate and equation data series 
    in a given figure dictionary using the provided range dictionary.

    Args:
        fig_dict (dict): The original figure dictionary containing various data series.
        range_dict (dict): A dictionary with keys "min_x" and "max_x" providing the 
                           global minimum and maximum x values for updates.

    Returns:
        dict: A new figure dictionary with updated x_range_default values for 
              equation and simulate series, while keeping other data unchanged.
    
    Notes:
        - If min_x or max_x in range_dict is None, the function preserves the 
          existing x_range_default values instead of overwriting them.
        - Uses deepcopy to ensure modifications do not affect the original fig_dict.
    """
    import copy  # Import inside function to limit scope

    updated_fig_dict = copy.deepcopy(fig_dict)  # Deep copy avoids modifying original data

    min_x = range_dict["min_x"]
    max_x = range_dict["max_x"]

    for data_series in updated_fig_dict.get("data", []):
        if "equation" in data_series:
            equation_info = data_series["equation"]

            # Determine valid values before assignment
            min_x_value = min_x if (min_x is not None) else equation_info.get("x_range_default", [None, None])[0]
            max_x_value = max_x if (max_x is not None) else equation_info.get("x_range_default", [None, None])[1]

            # Assign updated values
            equation_info["x_range_default"] = [min_x_value, max_x_value]
        
        elif "simulate" in data_series:
            simulate_info = data_series["simulate"]

            # Determine valid values before assignment
            min_x_value = min_x if (min_x is not None) else simulate_info.get("x_range_default", [None, None])[0]
            max_x_value = max_x if (max_x is not None) else simulate_info.get("x_range_default", [None, None])[1]

            # Assign updated values
            simulate_info["x_range_default"] = [min_x_value, max_x_value]

    return updated_fig_dict




def get_fig_dict_ranges(fig_dict, skip_equations=False, skip_simulations=False):
    """
    Extracts minimum and maximum x/y values from each data_series in a fig_dict, as well as overall min and max for x and y.

    Args:
        fig_dict (dict): The figure dictionary containing multiple data series.
        skip_equations (bool): If True, equation-based data series are ignored.
        skip_simulations (bool): If True, simulation-based data series are ignored.

    Returns:
        tuple: 
            - fig_dict_ranges (dict): A dictionary containing overall min/max x/y values across all valid series.
            - data_series_ranges (dict): A dictionary with individual min/max values for each data series.

    Notes:
        - Equations and simulations have predefined x-range defaults and limits.
        - If their x-range is absent, individual data series values are used.
        - Ensures empty lists don't trigger errors when computing min/max values.
    """
    # Initialize final range values to None to ensure assignment
    fig_dict_ranges = {
        "min_x": None,
        "max_x": None,
        "min_y": None,
        "max_y": None
    }

    data_series_ranges = {
        "min_x": [],
        "max_x": [],
        "min_y": [],
        "max_y": []
    }

    for data_series in fig_dict.get("data", []):
        min_x, max_x, min_y, max_y = None, None, None, None  # Initialize extrema as None

        # Determine if the data series contains either "equation" or "simulate"
        if "equation" in data_series:
            if skip_equations:
                implicit_data_series_to_extract_from = None
                pass  # Skip processing, but still append None values
            else:
                implicit_data_series_to_extract_from = data_series["equation"]
        
        elif "simulate" in data_series:
            if skip_simulations:
                implicit_data_series_to_extract_from = None
                pass  # Skip processing, but still append None values
            else:
                implicit_data_series_to_extract_from = data_series["simulate"]
        
        else:
            implicit_data_series_to_extract_from = None  # No equation or simulation, process x and y normally

        if implicit_data_series_to_extract_from:
            x_range_default = implicit_data_series_to_extract_from.get("x_range_default", [None, None]) 
            x_range_limits = implicit_data_series_to_extract_from.get("x_range_limits", [None, None]) 

            # Assign values, but keep None if missing
            min_x = (x_range_default[0] if (x_range_default[0] is not None) else x_range_limits[0])
            max_x = (x_range_default[1] if (x_range_default[1] is not None) else x_range_limits[1])

        # Ensure "x" key exists AND list is not empty before calling min() or max()
        if (min_x is None) and ("x" in data_series) and (len(data_series["x"]) > 0):  
            valid_x_values = [x for x in data_series["x"] if x is not None]  # Filter out None values
            if valid_x_values:  # Ensure list isn't empty after filtering
                min_x = min(valid_x_values)  

        if (max_x is None) and ("x" in data_series) and (len(data_series["x"]) > 0):  
            valid_x_values = [x for x in data_series["x"] if x is not None]  # Filter out None values
            if valid_x_values:  # Ensure list isn't empty after filtering
                max_x = max(valid_x_values)  

        # Ensure "y" key exists AND list is not empty before calling min() or max()
        if (min_y is None) and ("y" in data_series) and (len(data_series["y"]) > 0):  
            valid_y_values = [y for y in data_series["y"] if y is not None]  # Filter out None values
            if valid_y_values:  # Ensure list isn't empty after filtering
                min_y = min(valid_y_values)  

        if (max_y is None) and ("y" in data_series) and (len(data_series["y"]) > 0):  
            valid_y_values = [y for y in data_series["y"] if y is not None]  # Filter out None values
            if valid_y_values:  # Ensure list isn't empty after filtering
                max_y = max(valid_y_values)  

        # Always add values to the lists, including None if applicable
        data_series_ranges["min_x"].append(min_x)
        data_series_ranges["max_x"].append(max_x)
        data_series_ranges["min_y"].append(min_y)
        data_series_ranges["max_y"].append(max_y)

    # Filter out None values for overall min/max calculations
    valid_min_x_values = [x for x in data_series_ranges["min_x"] if x is not None]
    valid_max_x_values = [x for x in data_series_ranges["max_x"] if x is not None]
    valid_min_y_values = [y for y in data_series_ranges["min_y"] if y is not None]
    valid_max_y_values = [y for y in data_series_ranges["max_y"] if y is not None]

    fig_dict_ranges["min_x"] = min(valid_min_x_values) if valid_min_x_values else None
    fig_dict_ranges["max_x"] = max(valid_max_x_values) if valid_max_x_values else None
    fig_dict_ranges["min_y"] = min(valid_min_y_values) if valid_min_y_values else None
    fig_dict_ranges["max_y"] = max(valid_max_y_values) if valid_max_y_values else None

    return fig_dict_ranges, data_series_ranges


# # Example usage
# fig_dict = {
#     "data": [
#         {"x": [1, 2, 3, 4], "y": [10, 20, 30, 40]},
#         {"x": [5, 6, 7, 8], "y": [50, 60, 70, 80]},
#         {"equation": {
#             "x_range_default": [None, 500],
#             "x_range_limits": [100, 600]
#         }},
#         {"simulate": {
#             "x_range_default": [None, 700],
#             "x_range_limits": [300, 900]
#         }}
#     ]
# }

# fig_dict_ranges, data_series_ranges = get_fig_dict_ranges(fig_dict, skip_equations=True, skip_simulations=True)  # Skips both
# print("Data Series Values:", data_series_ranges)
# print("Extreme Values:", fig_dict_ranges)

### Start of section of code with functions for extracting and updating x and y ranges of data series ###


### Start section of code with functions for cleaning fig_dicts for plotly compatibility ###

def update_title_field(fig_dict, depth=1, max_depth=10):
    """ This function is intended to make JSONGrapher .json files compatible with the newer plotly recommended title field formatting
    which is necessary to do things like change the font, and also necessary for being able to convert a JSONGrapher json_dict to python plotly figure objects. """
    """ Recursively checks for 'title' fields and converts them to dictionary format. """
    if depth > max_depth or not isinstance(fig_dict, dict):
        return fig_dict
    
    for key, value in fig_dict.items():
        if key == "title" and isinstance(value, str):
            fig_dict[key] = {"text": value}
        elif isinstance(value, dict):  # Nested dictionary
            fig_dict[key] = update_title_field(value, depth + 1, max_depth)
        elif isinstance(value, list):  # Lists can contain nested dictionaries
            fig_dict[key] = [update_title_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in value]
    
    return fig_dict

def remove_extra_information_field(fig_dict, depth=1, max_depth=10):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGrapher json_dict to python plotly figure objects. """
    """Recursively checks for 'extraInformation' fields and removes them."""
    if depth > max_depth or not isinstance(fig_dict, dict):
        return fig_dict

    # Use a copy of the dictionary keys to safely modify the dictionary during iteration
    for key in list(fig_dict.keys()):
        if key == ("extraInformation" or "extra_information"):
            del fig_dict[key]  # Remove the field
        elif isinstance(fig_dict[key], dict):  # Nested dictionary
            fig_dict[key] = remove_extra_information_field(fig_dict[key], depth + 1, max_depth)
        elif isinstance(fig_dict[key], list):  # Lists can contain nested dictionaries
            fig_dict[key] = [
                remove_extra_information_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in fig_dict[key]
            ]
    
    return fig_dict
    

def remove_nested_comments(data, top_level=True):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGrapher json_dict to python plotly figure objects. """
    """Removes 'comments' fields that are not at the top level of the JSON-dict. Starts with 'top_level = True' when dict is first passed in then becomes false after that. """
    if not isinstance(data, dict):
        return data
    # Process nested structures
    for key in list(data.keys()):
        if isinstance(data[key], dict):  # Nested dictionary
            data[key] = remove_nested_comments(data[key], top_level=False)
        elif isinstance(data[key], list):  # Lists can contain nested dictionaries
            data[key] = [
                remove_nested_comments(item, top_level=False) if isinstance(item, dict) else item for item in data[key]
            ]
    # Only remove 'comments' if not at the top level
    if not top_level:
        data = {k: v for k, v in data.items() if k != "comments"}
    return data

def remove_simulate_field(json_fig_dict):
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('simulate', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_equation_field(json_fig_dict):
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('equation', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_trace_style_field(json_fig_dict):
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('trace_style', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
        data_dict.pop('tracetype', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_custom_units_chevrons(json_fig_dict):
    json_fig_dict['layout']['xaxis']['title']['text'] = json_fig_dict['layout']['xaxis']['title']['text'].replace('<','').replace('>','')
    json_fig_dict['layout']['yaxis']['title']['text'] = json_fig_dict['layout']['yaxis']['title']['text'].replace('<','').replace('>','')
    return json_fig_dict

def clean_json_fig_dict(json_fig_dict, fields_to_update=["title_field", "extraInformation", "nested_comments"]):
    """ This function is intended to make JSONGrapher .json files compatible with the current plotly format expectations
     and also necessary for being able to convert a JSONGrapher json_dict to python plotly figure objects. 
     This function can also remove the 'simulate' field from data series. However, that is not the default behavior
     because one would not want to do that by mistake before simulation is performed.
     This function can also remove the 'equation' field from data series. However, that is not the default behavior
     because one would not want to do that by mistake before the equation is evaluated.
     """
    fig_dict = json_fig_dict
    #unmodified_data = copy.deepcopy(data)
    if "title_field" in fields_to_update:
        fig_dict = update_title_field(fig_dict)
    if "extraInformation" in fields_to_update:
        fig_dict = remove_extra_information_field(fig_dict)
    if "nested_comments" in fields_to_update:
        fig_dict = remove_nested_comments(fig_dict)
    if "simulate" in fields_to_update:
        fig_dict = remove_simulate_field(fig_dict)
    if "equation" in fields_to_update:
        fig_dict = remove_equation_field(fig_dict)
    if "custom_units_chevrons" in fields_to_update:
        fig_dict = remove_custom_units_chevrons(fig_dict)
    if "trace_style" in fields_to_update:
        fig_dict = remove_trace_style_field(fig_dict)

    return fig_dict

### End section of code with functions for cleaning fig_dicts for plotly compatibility ###

### Beginning of section of file that has functions for "simulate" and "equation" fields, to evaluate equations and call external javascript simulators, as well as support functions ###

def run_js_simulation(javascript_simulator_url, simulator_input_json_dict, verbose = False):
    """
    Downloads a JavaScript file using its URL, extracts the filename, appends an export statement,
    executes it with Node.js, and parses the output.

    Parameters:
    javascript_simulator_url (str): URL of the raw JavaScript file to download and execute. Must have a function named simulate.
    simulator_input_json_dict (dict): Input parameters for the JavaScript simulator.

    # Example inputs
    javascript_simulator_url = "https://github.com/AdityaSavara/JSONGrapherExamples/blob/main/ExampleSimulators/Langmuir_Isotherm.js"
    simulator_input_json_dict = {
        "simulate": {
            "K_eq": None,
            "sigma_max": "1.0267670459667 (mol/kg)",
            "k_ads": "200 (1/(bar * s))",
            "k_des": "100 (1/s)"
        }
    }


    Returns:
    dict: Parsed JSON output from the JavaScript simulation, or None if an error occurred.
    """
    import requests
    import subprocess
    import json
    import os

    # Convert to raw GitHub URL only if "raw" is not in the original URL
    # For example, the first link below gets converted to the second one.
    # https://github.com/AdityaSavara/JSONGrapherExamples/blob/main/ExampleSimulators/Langmuir_Isotherm.js
    # https://raw.githubusercontent.com/AdityaSavara/JSONGrapherExamples/main/ExampleSimulators/Langmuir_Isotherm.js    
    
    if "raw" not in javascript_simulator_url:
        javascript_simulator_url = convert_to_raw_github_url(javascript_simulator_url)

    # Extract filename from URL
    js_filename = os.path.basename(javascript_simulator_url)

    # Download the JavaScript file
    response = requests.get(javascript_simulator_url)

    if response.status_code == 200:
        with open(js_filename, "w") as file:
            file.write(response.text)

        # Append the export statement to the JavaScript file
        with open(js_filename, "a") as file:
            file.write("\nmodule.exports = { simulate };")

        # Convert input dictionary to a JSON string
        input_json_str = json.dumps(simulator_input_json_dict)

        # Prepare JavaScript command for execution
        js_command = f"""
        const simulator = require('./{js_filename}');
        console.log(JSON.stringify(simulator.simulate({input_json_str})));
        """

        result = subprocess.run(["node", "-e", js_command], capture_output=True, text=True)

        # Print output and errors if verbose
        if verbose:
            print("Raw JavaScript Output:", result.stdout)
            print("Node.js Errors:", result.stderr)

        # Parse JSON if valid
        if result.stdout.strip():
            try:
                data_dict_with_simulation = json.loads(result.stdout) #This is the normal case.
                return data_dict_with_simulation
            except json.JSONDecodeError:
                print("Error: JavaScript output is not valid JSON.")
                return None
    else:
        print(f"Error: Unable to fetch JavaScript file. Status code {response.status_code}")
        return None

def convert_to_raw_github_url(url):
    """
    Converts a GitHub file URL to its raw content URL if necessary, preserving the filename.
    This function is really a support function for run_js_simulation
    """
    from urllib.parse import urlparse
    parsed_url = urlparse(url)

    # If the URL is already a raw GitHub link, return it unchanged
    if "raw.githubusercontent.com" in parsed_url.netloc:
        return url

    path_parts = parsed_url.path.strip("/").split("/")

    # Ensure it's a valid GitHub file URL
    if "github.com" in parsed_url.netloc and len(path_parts) >= 4:
        if path_parts[2] == "blob":  
            # If the URL contains "blob", adjust extraction
            user, repo, branch = path_parts[:2] + [path_parts[3]]
            file_path = "/".join(path_parts[4:])  # Keep full file path including filename
        else:
            # Standard GitHub file URL (without "blob")
            user, repo, branch = path_parts[:3]
            file_path = "/".join(path_parts[3:])  # Keep full file path including filename

        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

    return url  # Return unchanged if not a GitHub file URL

#This function takes in a data_series_dict object and then
#calls an external javascript simulation if needed
#Then fills the data_series dict with the simulated data.
#This function is not intended to be called by the regular user
#because it returns extra fields that need to be parsed out.
#and because it does not do unit conversions as needed after the simulation resultss are returned.
def simulate_data_series(data_series_dict, simulator_link='', verbose=False):
    if simulator_link == '':
        simulator_link = data_series_dict["simulate"]["model"]  
    try:
        simulation_return = run_js_simulation(simulator_link, data_series_dict, verbose=verbose)
        if isinstance(simulation_return, dict) and "error" in simulation_return: # Check for errors in the returned data
            print(f"Simulation failed: {simulation_return.get('error_message', 'Unknown error')}")
            print(simulation_return)
            return None
        return simulation_return.get("data", None)

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

#Function that goes through a fig_dict data series and simulates each data series as needed.
#If the simulated data returned has "x_label" and/or "y_label" with units, those will be used to scale the data, then will be removed.
def simulate_as_needed_in_fig_dict(fig_dict, simulator_link='', verbose=False):
    data_dicts_list = fig_dict['data']    
    for data_dict_index in range(len(data_dicts_list)):
        fig_dict = simulate_specific_data_series_by_index(fig_dict, data_dict_index, simulator_link=simulator_link, verbose=verbose)
    return fig_dict

#Function that takes fig_dict and dataseries index and simulates if needed. Also performs unit conversions as needed.
#If the simulated data returned has "x_label" and/or "y_label" with units, those will be used to scale the data, then will be removed.
def simulate_specific_data_series_by_index(fig_dict, data_series_index, simulator_link='', verbose=False):
    data_dicts_list = fig_dict['data']
    data_dict_index = data_series_index
    data_dict = data_dicts_list[data_dict_index]
    if 'simulate' in data_dict:
        data_dict_filled = simulate_data_series(data_dict, simulator_link=simulator_link, verbose=verbose)
        # Check if unit scaling is needed
        if ("x_label" in data_dict_filled) or ("y_label" in data_dict_filled):
            #first, get the units that are in the layout of fig_dict so we know what to convert to.
            existing_record_x_label = fig_dict["layout"]["xaxis"]["title"]["text"]
            existing_record_y_label = fig_dict["layout"]["yaxis"]["title"]["text"]
            # Extract units  from the simulation output.
            existing_record_x_units = separate_label_text_from_units(existing_record_x_label).get("units", "")
            existing_record_y_units = separate_label_text_from_units(existing_record_y_label).get("units", "")
            simulated_data_series_x_units = separate_label_text_from_units(data_dict_filled.get('x_label', '')).get("units", "")
            simulated_data_series_y_units = separate_label_text_from_units(data_dict_filled.get('y_label', '')).get("units", "")
            # Compute unit scaling ratios
            x_units_ratio = get_units_scaling_ratio(simulated_data_series_x_units, existing_record_x_units) if simulated_data_series_x_units and existing_record_x_units else 1
            y_units_ratio = get_units_scaling_ratio(simulated_data_series_y_units, existing_record_y_units) if simulated_data_series_y_units and existing_record_y_units else 1
            # Apply scaling to the data series
            scale_dataseries_dict(data_dict_filled, num_to_scale_x_values_by=x_units_ratio, num_to_scale_y_values_by=y_units_ratio)
            #Verbose logging for debugging
            if verbose:
                print(f"Scaling X values by: {x_units_ratio}, Scaling Y values by: {y_units_ratio}")
            #Now need to remove the "x_label" and "y_label" to be compatible with plotly.
            data_dict_filled.pop("x_label", None)
            data_dict_filled.pop("y_label", None)
        # Update the figure dictionary
        data_dicts_list[data_dict_index] = data_dict_filled
    fig_dict['data'] = data_dicts_list
    return fig_dict

def evaluate_equations_as_needed_in_fig_dict(fig_dict):
    data_dicts_list = fig_dict['data']
    for data_dict_index, data_dict in enumerate(data_dicts_list):
        if 'equation' in data_dict:
            fig_dict = evaluate_equation_for_data_series_by_index(fig_dict, data_dict_index)
    return fig_dict

def evaluate_equation_for_data_series_by_index(fig_dict, data_series_index, verbose=False):   
    try:
        import json_equationer.equation_evaluator as equation_evaluator
        import json_equationer.equation_creator  as equation_creator
    except:
        from . import equation_evaluator
        from . import equation_creator
    import copy
    data_dicts_list = fig_dict['data']
    data_dict = data_dicts_list[data_series_index]
    if 'equation' in data_dict:
        equation_object = equation_creator.Equation(data_dict['equation'])
        equation_dict_evaluated = equation_object.evaluate_equation()
        data_dict_filled = copy.deepcopy(data_dict)
        data_dict_filled['equation'] = equation_dict_evaluated
        data_dict_filled['x_label'] = data_dict_filled['equation']['x_variable'] 
        data_dict_filled['y_label'] = data_dict_filled['equation']['y_variable'] 
        data_dict_filled['x'] = equation_dict_evaluated['x_points']
        data_dict_filled['y'] = equation_dict_evaluated['y_points']
        #data_dict_filled may include "x_label" and/or "y_label". If it does, we'll need to check about scaling units.
        if (("x_label" in data_dict_filled) or ("y_label" in data_dict_filled)):
            #first, get the units that are in the layout of fig_dict so we know what to convert to.
            existing_record_x_label = fig_dict["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            existing_record_y_label = fig_dict["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            existing_record_x_units = separate_label_text_from_units(existing_record_x_label)["units"]
            existing_record_y_units = separate_label_text_from_units(existing_record_y_label)["units"]
            if (existing_record_x_units == '') and (existing_record_y_units == ''): #skip scaling if there are no units.
                pass
            else: #If we will be scaling...
                #now, get the units from the evaluated equation output.
                simulated_data_series_x_units = separate_label_text_from_units(data_dict_filled['x_label'])["units"]
                simulated_data_series_y_units = separate_label_text_from_units(data_dict_filled['y_label'])["units"]
                x_units_ratio = get_units_scaling_ratio(simulated_data_series_x_units, existing_record_x_units)
                y_units_ratio = get_units_scaling_ratio(simulated_data_series_y_units, existing_record_y_units)
                #We scale the dataseries, which really should be a function.
                scale_dataseries_dict(data_dict_filled, num_to_scale_x_values_by = x_units_ratio, num_to_scale_y_values_by = y_units_ratio)
            #Now need to remove the "x_label" and "y_label" to be compatible with plotly.
            data_dict_filled.pop("x_label", None)
            data_dict_filled.pop("y_label", None)
        data_dict_filled['type'] = 'spline'
        data_dicts_list[data_series_index] = data_dict_filled
    fig_dict['data'] = data_dicts_list
    return fig_dict


def update_implicit_data_series_data(target_fig_dict, source_fig_dict, parallel_structure=True, modify_target_directly = False):
    """
    Updates the x and y values of implicit data series (equation/simulate) in target_fig_dict 
    using values from the corresponding series in source_fig_dict.

    Args:
        target_fig_dict (dict): The figure dictionary that needs updated data.
        source_fig_dict (dict): The figure dictionary that provides x and y values.
        parallel_structure (bool, optional): If True, assumes both data lists are the same 
                                             length and updates using zip(). If False, 
                                             matches by name instead. Default is True.

    Returns:
        dict: A new figure dictionary with updated x and y values for implicit data series.

    Notes:
        - If parallel_structure=True and both lists have the same length, updates use zip().
        - If parallel_structure=False, matching is done by the "name" field.
        - Only updates data series that contain "simulate" or "equation".
        - Ensures deep copying to avoid modifying the original structures.
    """
    if modify_target_directly == False:
        import copy  # Import inside function to limit scope   
        updated_fig_dict =  copy.deepcopy(target_fig_dict)  # Deep copy to avoid modifying original
    if modify_target_directly == True:
        updated_fig_dict = target_fig_dict

    target_data_series = updated_fig_dict.get("data", [])
    source_data_series = source_fig_dict.get("data", [])

    if parallel_structure and len(target_data_series) == len(source_data_series):
        # Use zip() when parallel_structure=True and lengths match
        for target_series, source_series in zip(target_data_series, source_data_series):
            if ("equation" in target_series) or ("simulate" in target_series):
                target_series["x"] = source_series.get("x", [])  # Extract and apply "x" values
                target_series["y"] = source_series.get("y", [])  # Extract and apply "y" values
    else:
        # Match by name when parallel_structure=False or lengths differ
        source_data_dict = {series["name"]: series for series in source_data_series if "name" in series}

        for target_series in target_data_series:
            if ("equation" in target_series) or ("simulate" in target_series):
                target_name = target_series.get("name")
                
                if target_name in source_data_dict:
                    source_series = source_data_dict[target_name]
                    target_series["x"] = source_series.get("x", [])  # Extract and apply "x" values
                    target_series["y"] = source_series.get("y", [])  # Extract and apply "y" values

    return updated_fig_dict


def execute_implicit_data_series_operations(fig_dict, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
    """
    This function is designed to be called during creation of a plotly or matplotlib figure creation.
    Processes implicit data series (equation/simulate), adjusting ranges, performing simulations,
    and evaluating equations as needed.

    The important thing is that this function creates a "fresh" fig_dict, does some manipulation, then then gets the data from that
    and adds it to the original fig_dict.
    That way the original fig_dict is not changed other than getting the simulated/evaluated data.

    The reason the function works this way is that the x_range_default of the implicit data series (equations and simulations)
    are adjusted to match the data in the fig_dict, but we don't want to change the x_range_default of our main record.
    That's why we make a copy for creating simulated/evaluated data from those adjusted ranges, and then put the simulated/evaluated data
    back into the original dict.

    

    Args:
        fig_dict (dict): The figure dictionary containing data series.
        simulate_all_series (bool): If True, performs simulations for applicable series.
        evaluate_all_equations (bool): If True, evaluates all equation-based series.
        adjust_implicit_data_ranges (bool): If True, modifies ranges for implicit data series.

    Returns:
        dict: Updated figure dictionary with processed implicit data series.

    Notes:
        - If adjust_implicit_data_ranges=True, retrieves min/max values from regular data series 
          (those that are not equations and not simulations) and applies them to implicit data.
        - If simulate_all_series=True, executes simulations for all series that require them 
          and transfers the computed data back to fig_dict without copying ranges.
        - If evaluate_all_equations=True, solves equations as needed and transfers results 
          back to fig_dict without copying ranges.
        - Uses deepcopy to avoid modifying the original input dictionary.
    """
    import copy  # Import inside function for modularity

    # Create a copy for processing implicit series separately
    fig_dict_for_implicit = copy.deepcopy(fig_dict)

    
    if adjust_implicit_data_ranges:
        # Retrieve ranges from data series that are not equation-based or simulation-based.
        fig_dict_ranges, data_series_ranges = get_fig_dict_ranges(fig_dict, skip_equations=True, skip_simulations=True)
        # Apply the extracted ranges to implicit data series before simulation or equation evaluation.
        fig_dict_for_implicit = update_implicit_data_series_x_ranges(fig_dict, fig_dict_ranges)

    if simulate_all_series:
        # Perform simulations for applicable series
        fig_dict_for_implicit = simulate_as_needed_in_fig_dict(fig_dict_for_implicit)
        # Copy data back to fig_dict, ensuring ranges remain unchanged
        fig_dict = update_implicit_data_series_data(target_fig_dict=fig_dict, source_fig_dict=fig_dict_for_implicit, parallel_structure=True, modify_target_directly=True)

    if evaluate_all_equations:
        # Evaluate equations that require computation
        fig_dict_for_implicit = evaluate_equations_as_needed_in_fig_dict(fig_dict_for_implicit)
        # Copy results back without overwriting the ranges
        fig_dict = update_implicit_data_series_data(target_fig_dict=fig_dict, source_fig_dict=fig_dict_for_implicit, parallel_structure=True, modify_target_directly=True)

    return fig_dict



### End of section of file that has functions for "simulate" and "equation" fields, to evaluate equations and call external javascript simulators, as well as support functions###

# Example Usage
if __name__ == "__main__":
    # Example of creating a record with optional attributes.
    Record = JSONGrapherRecord(
        comments="Here is a description.",
        graph_title="Here Is The Graph Title Spot",
        data_objects_list=[
            {"comments": "Initial data series.", "uid": "123", "name": "Series A", "trace_type": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    )
    x_label_including_units= "Time (years)" 
    y_label_including_units = "Height (m)"
    Record.set_comments("Tree Growth Data collected from the US National Arboretum")
    Record.set_datatype("Tree_Growth_Curve")
    Record.set_x_axis_label_including_units(x_label_including_units)
    Record.set_y_axis_label_including_units(y_label_including_units)


    Record.export_to_json_file("test.json")

    print(Record)

    # Example of creating a record from an existing dictionary.
    existing_JSONGrapher_record = {
        "comments": "Existing record description.",
        "graph_title": "Existing Graph",
        "data": [
            {"comments": "Data series 1", "uid": "123", "name": "Series A", "type": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    }
    Record_from_existing = JSONGrapherRecord(existing_JSONGrapher_record=existing_JSONGrapher_record)
    x_label_including_units= "Time (years)" 
    y_label_including_units = "Height (cm)"
    Record_from_existing.set_comments("Tree Growth Data collected from the US National Arboretum")
    Record_from_existing.set_datatype("Tree_Growth_Curve")
    Record_from_existing.set_x_axis_label_including_units(x_label_including_units)
    Record_from_existing.set_y_axis_label_including_units(y_label_including_units)
    print(Record_from_existing)
    
    print("NOW WILL MERGE THE RECORDS, AND USE THE SECOND ONE TWICE (AS A JSONGrapher OBJECT THEN JUST THE FIG_DICT)")
    print(merge_JSONGrapherRecords([Record, Record_from_existing, Record_from_existing.fig_dict]))


