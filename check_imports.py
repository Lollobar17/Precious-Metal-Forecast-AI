import importlib
modules = ['m01_data_loader','m02_processor','m03_model','m04_main',
           'm05_v2_data_loader','m06_v2_model','m07_v2_backtester','m08_v2_main',
           'm09_v3_hyper_optimizer','m10_v3_forecaster','m11_v4_live_updater','m12_v4_all_in_one',
           'm13_rebuild_snapshot','m14_retrain_models','m15_run_full_retrain','m16_inspect_snapshot']


for m in modules:
    try:
        importlib.import_module(m)
        print(m, 'imported successfully')
    except Exception as e:
        print(m, 'failed to import:', e)
