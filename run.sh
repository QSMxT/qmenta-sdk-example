rm -rf analysis_output
mkdir analysis_output

# test data needs to be in folder example_data
# subfolder: input_0 -> mag.zip (https://files.osf.io/v1/resources/ru43c/providers/osfstorage/62255367d3db13037a7e734c?action=download&direct&version=1)
# subfolder: input_1 -> phs.zip (https://files.osf.io/v1/resources/ru43c/providers/osfstorage/6225536bd3db13037c7e7136?action=download&direct&version=1)

docker build -t astewartau/qsmxt_qmenta:1.3.5_20230308 -f qsm.Dockerfile .

python test_tool.py astewartau/qsmxt_qmenta:1.3.5_20230308 example_data analysis_output \
    --settings settings.json \
    --values mock_settings_values.json

