rm -rf analysis_output
mkdir analysis_output

docker build -t stebo85/qsmxtqmenta:211008 -f qsm.Dockerfile .

python test_tool.py stebo85/qsmxtqmenta:211008 example_data analysis_output \
    --settings settings.json \
    --values mock_settings_values.json