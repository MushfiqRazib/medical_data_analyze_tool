#
# File: main.py
# Author: Muhammad Mushfiqur Rahman
# Description: Medical app data visualization tool - summary info, churn rate, retention rate etc.
# Email:mushfiq.rahman@tum.de
# Date 2018-05-22

from data_visualize_analyze import DatasetVisualize

def main():
    data_vis = DatasetVisualize()
    # set and load dataset information.
    data_vis.init_process_dataset()

    # processing dataset general summary info
    print('\nProcessing dataset general summary...')
    data_vis.process_dataset_for_general_summary_1()
    data_vis.process_dataset_for_general_summary_2()

    # dataset summary visualization
    print('\nVisualizing dataset summary information...')
    data_vis.dataset_summary_diagram_1()
    data_vis.dataset_summary_diagram_2()
    data_vis.dataset_summary_diagram_3()

    # processing dataset retention visualization
    print('\nProcessing dataset retention calculation...')
    data_vis.process_dataset_for_n_day_retention()
    data_vis.process_dataset_for_weekly_retention_visualization()
    data_vis.process_dataset_for_30days_retention_visualization()

    # dataset retention visualization
    print('\nVisualizing dataset retention diagram...')
    data_vis.dataset_weekly_retention_visualization()
    data_vis.dataset_30days_retention_visualization()
    data_vis.dataset_retention_diagram_1()
    data_vis.dataset_retention_diagram_2()
    data_vis.dataset_retention_diagram_3()

    # dataset pattern/trend visualization
    print('\nVisualizing dataset activity patterns...')
    data_vis.dataset_user_activity_trend_diagram_1()
    data_vis.dataset_user_activity_trend_diagram_2()

if __name__ == "__main__":
    main()
