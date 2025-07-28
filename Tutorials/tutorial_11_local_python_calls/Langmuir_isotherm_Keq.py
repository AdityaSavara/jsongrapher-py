import json
import copy
# #### Add the relative path to the units_helper.parse_units module for convenience ####
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import units_helper

## The function you make should expect to receive a JSON-like dictionary or JSON-like string.
## You can name this function whatever you want.
def simulate(input_dict):
    # Ensure the input is valid json by converting it back and forth to a string.
    try:
        input_dict = json.dumps(input_dict)
        input_dict = json.loads(input_dict)
    except:
        raise TypeError("Input data is not valid JSON.")

    # Extract simulation parameters
    simulation_parameters = input_dict["simulate"]  # Accessing directly

    # Use K_eq provided in the input
    K_eq_obj = units_helper.parse_units(simulation_parameters["K_eq"])

    #Set sigma max
    if "sigma_max" in simulation_parameters:
        sigma_max = simulation_parameters["sigma_max"]  
    else:
        sigma_max = "1(<Monolayer>)"
    sigma_max_value_and_units = units_helper.parse_units(sigma_max)

    # This is the actual "simulation"
    def get_predicted_values(K_eq_value, K_eq_unit, sigma_max=1, sigma_max_unit="<Monolayer>"):
        x_label = f"Pressure (({K_eq_unit})**(-1))"
        y_label = f"Amount Adsorbed ({sigma_max_unit})"
        y_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] #For our langmuir simulation we use Y to get X in this case. Coverage to calculate pressure.
        x_values = [sigma_max * y / (K_eq_value * (1 - y)) for y in y_values]
        
        predicted_values = {
            "x_values": x_values,
            "y_values": y_values,
            "x_label": x_label,
            "y_label": y_label
        }
        return predicted_values

    # This calls the helper function get_predicted_values to do the simulation.
    # We don't need input_data here, we are just passing it through with the simulation.
    def run_simulation(input_data, K_eq_obj, sigma_max_value_and_units):
        predicted_values = get_predicted_values(K_eq_obj["value"], K_eq_obj["units"], sigma_max_value_and_units["value"], sigma_max_value_and_units["units"])
        return predicted_values

    # Main workflow
    simulation_result = run_simulation(input_dict, K_eq_obj, sigma_max_value_and_units)

    #initialize the output dictionary 
    output_as_json_dict = {}
    #Add in some messaging that is useful but not necessary.
    output_as_json_dict["success"] = True
    output_as_json_dict["message"] = "Simulation completed successfully"
    #Make a data subfield which starts as a deep copy of the input dictionary.
    output_as_json_dict["data"] ={}
    output_as_json_dict["data"]["simulate"] = copy.deepcopy(input_dict) #this returns the inputs we started with.
    output_as_json_dict["data"]["x"] = simulation_result["x_values"]
    output_as_json_dict["data"]["y"] = simulation_result["y_values"]
    output_as_json_dict["data"]["x_label"] = simulation_result["x_label"]
    output_as_json_dict["data"]["y_label"] = simulation_result["y_label"]

    #Ensure the output is valid json by converting it back and forth to a string then dictionary.
    output_as_json_string = json.dumps(output_as_json_dict, indent=4) 
    output_as_json_dict_checked = json.loads(output_as_json_string)  
    return output_as_json_dict_checked
                      
if __name__ == "__main__":
    ##### Test with input as a JSON-like dictionary.#####
    input_json_as_dict = {
        "simulate": {
            "K_eq": "99.6 (bar**(-1))",  # Using K_eq directly instead of k_ads and k_des
            "sigma_max": "1.0267670459667 (mol*kg^(-1))",
            "simulation_function_label": "simulate_Langmuir_by_Keq"
        }
    }
    output_dict = simulate(input_json_as_dict)  #testing with call to the primary function of this file.
    #we can make the output look nicer for printing by converting to a string that has indents.
    output_as_json_string = json.dumps(output_dict, indent=4)
    print("\nOutput from JSON dictionary input: \n", output_as_json_string)

    ##### Test wtih input from a JSONGrapher file #####
    # Specify the path to your JSON file
    JSONGrapher_record_file_path = './343_equilibrium.json'
    ### The rest of this code will does not need to be changed. It will always load the simulate field from the first index.##
    with open(JSONGrapher_record_file_path, 'r') as file:
        # Load the JSON data into a Python dictionary
        JSONGrapher_record_dict = json.load(file)
    #extract the simulate sub-JSON from the first entry in "data", which is (index 0).
    simulate_dict_from_JSONGrapher_record = JSONGrapher_record_dict["data"][0]['simulate']
    #Now use this for our input dictionary, recalling that "simulate" must be a key in that dictionary.
    input_json_as_dict = {"simulate": simulate_dict_from_JSONGrapher_record}
    output_dict = simulate(input_json_as_dict)  #testing with call to the primary function of this file.
    #We can make the output look nicer for printing by converting to a string that has indents.
    output_as_json_string = json.dumps(output_dict, indent=4)
    print("\nOutput from JSONGrapher file: \n", output_as_json_string)


    # Expected Output:
    # Identical outputs for both inputs:
    #  {
    #     "success": true,
    #     "message": "Simulation completed successfully",
    #     "data": {
    #         "simulate": {
    #             "simulate": {
    #                 "K_eq": "5.0(L/mol)",
    #                 "sigma_max": "1.2(<Monolayer>)",
    #                 "simulation_function_label": "simulate_Langmuir_by_Keq"
    #             }
    #         },
    #         "x": [
    #             0.026666666666666665,
    #             0.06,
    #             0.10285714285714286,
    #             0.16,
    #             0.24,
    #             0.36,
    #             0.5599999999999999,
    #             0.9600000000000002,
    #             2.1600000000000006
    #         ],
    #         "y": [
    #             0.1,
    #             0.2,
    #             0.3,
    #             0.4,
    #             0.5,
    #             0.6,
    #             0.7,
    #             0.8,
    #             0.9
    #         ],
    #         "x_label": "Pressure (1/(L/mol))",
    #         "y_label": "Amount Adsorbed (<Monolayer>)"
    #     }
    # }