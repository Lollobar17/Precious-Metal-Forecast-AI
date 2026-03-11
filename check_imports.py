import importlib
modules = ['m1_data_loader','m2_processor','m3_model','m4_main',
           'm5_v2_data_loader','m6_v2_model','m7_v2_backtester','m8_v2_main',
           'm9_v3_hyper_optimizer','m10_v3_forecaster','m11_v4_live_updater','m12_v4_all_in_one',
           'm13_rebuild_snapshot','m14_retrain_models','m15_run_full_retrain','m16_inspect_snapshot']


for m in modules:
    try:
        importlib.import_module(m)
        print(m, 'imported successfully')
    except Exception as e:
        print(m, 'failed to import:', e)
