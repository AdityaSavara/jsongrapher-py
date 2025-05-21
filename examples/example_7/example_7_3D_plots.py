import JSONGrapher

scatter3d_record = JSONGrapher.import_JSONGrapherRecords(["Scatter3d.json"])
scatter3d_record.plot()

Surface3d_record = JSONGrapher.import_JSONGrapherRecords(["Surface3d.json"])
Surface3d_record.plot()