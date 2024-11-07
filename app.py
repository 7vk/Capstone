from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import io

app = Flask(__name__)

# Global variable to store the warning message
warning_message = ""

# Global variable to store the graphs
graphs = {}

# Hardcoded altitude data
altitude_data = [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 0} for i in range(2)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 1} for i in range(2, 8)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 2} for i in range(8, 13)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 3} for i in range(13, 19)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 4} for i in range(19, 25)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 5} for i in range(25, 31)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 6} for i in range(31, 37)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 7} for i in range(37, 43)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 8} for i in range(43, 49)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 9} for i in range(49, 55)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 10} for i in range(55, 61)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 11} for i in range(61, 67)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 12} for i in range(67, 73)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 13} for i in range(73, 79)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 14} for i in range(79, 85)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 15} for i in range(85, 91)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 16} for i in range(91, 97)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 17} for i in range(97, 103)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 18} for i in range(103, 109)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 19} for i in range(109, 115)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 20} for i in range(115, 121)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 21} for i in range(121, 127)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 22} for i in range(127, 133)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 23} for i in range(133, 139)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 24} for i in range(139, 145)
] + [
    {"time": f"00:00:{str(i).zfill(2)}", "altitude": 25} for i in range(145, 151)
]

def parse_data(file_content, temperature, humidity):
    global warning_message
    data = []
    
    print("Starting to parse data...")  # Debug print
    
    # Split content into lines and remove empty lines
    lines = [line.strip() for line in file_content.split('\n') if line.strip()]
    print(f"Number of lines to process: {len(lines)}")  # Debug print
    
    for line in lines:
        # Skip the "SD card initialized" line and "Data saved" lines
        if "SD card" in line or "Data saved" in line:
            continue
            
        if "Time:" in line:
            try:
                print(f"Processing line: {line}")  # Debug print
                
                # Split the line by pipe
                parts = [part.strip() for part in line.split('|')]
                print(f"Parts after splitting: {parts}")  # Debug print
                
                # Extract time
                time = parts[0].replace("Time:", "").strip()
                print(f"Extracted time: {time}")  # Debug print
                
                # Extract CO concentration
                co_part = parts[1].replace("CO Concentration:", "").replace("ppm", "").strip()
                co = float(co_part)
                print(f"Extracted CO: {co}")  # Debug print
                
                # Extract H2 concentration
                h2_part = parts[2].replace("H2 Concentration:", "").replace("ppm", "").strip()
                h2 = float(h2_part)
                print(f"Extracted H2: {h2}")  # Debug print
                
                # Extract Dust concentration
                dust_part = parts[3].replace("Dust Concentration:", "").replace("µg/m³", "").strip()
                dust = float(dust_part)
                print(f"Extracted Dust: {dust}")  # Debug print
                
                data_point = {
                    'Time': time,
                    'CO': co,
                    'H2': h2,
                    'Dust': dust
                }
                print(f"Created data point: {data_point}")  # Debug print
                
                data.append(data_point)
                
            except Exception as e:
                print(f"Error processing line: {line}")
                print(f"Error details: {str(e)}")
                print(f"Exception type: {type(e)}")
                continue
    
    print(f"Total data points collected: {len(data)}")  # Debug print
    
    if not data:
        raise ValueError("No valid data was parsed from the file")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print(f"DataFrame created with shape: {df.shape}")  # Debug print
    
    # Add temperature and humidity if provided
    if temperature:
        df['Temperature'] = float(temperature)
    if humidity:
        df['Humidity'] = float(humidity)
    
    print("Data parsing completed successfully")  # Debug print
    return df

def create_detailed_graphs(df):
    graphs = {}
    
    # 1. Time series subplot (existing)
    fig_time = make_subplots(rows=3, cols=1, 
                       subplot_titles=('CO Concentration vs Time', 
                                     'H2 Concentration vs Time',
                                     'Dust Concentration vs Time'))
    
    fig_time.add_trace(go.Scatter(x=df['Time'], y=df['CO'], 
                            name='CO', line=dict(color='red')), row=1, col=1)
    fig_time.add_trace(go.Scatter(x=df['Time'], y=df['H2'], 
                            name='H2', line=dict(color='blue')), row=2, col=1)
    fig_time.add_trace(go.Scatter(x=df['Time'], y=df['Dust'], 
                            name='Dust', line=dict(color='green')), row=3, col=1)
    
    fig_time.update_layout(height=900, title_text="Air Quality Metrics Over Time",
                     showlegend=True, legend_title="Metrics")
    graphs['time_series'] = pio.to_json(fig_time)

    # 2. 3D Scatter Plot
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=df['CO'],
        y=df['H2'],
        z=df['Dust'],
        mode='markers',
        marker=dict(
            size=8,
            color=df.index,
            colorscale='Viridis',
            opacity=0.8
        ),
        text=df['Time'],
        hovertemplate="Time: %{text}<br>CO: %{x}<br>H2: %{y}<br>Dust: %{z}<extra></extra>"
    )])

    fig_3d.update_layout(
        title="3D Visualization of Sensor Data",
        scene=dict(
            xaxis_title="CO (ppm)",
            yaxis_title="H2 (ppm)",
            zaxis_title="Dust (µg/m³)"
        ),
        height=800
    )
    graphs['scatter_3d'] = pio.to_json(fig_3d)

    # 3. Create altitude-based visualizations
    try:
        # Convert altitude data to DataFrame
        altitude_df = pd.DataFrame(altitude_data)
        
        # Create a copy of df with lowercase 'time' column for merging
        df_for_merge = df.copy()
        df_for_merge['time'] = df_for_merge['Time']  # Create lowercase version for merging
        
        # Merge sensor data with altitude data based on time
        merged_df = pd.merge(df_for_merge, altitude_df, on='time', how='left')
        
        if merged_df['altitude'].isna().all():
            print("Warning: No matching altitude data found")
            return graphs  # Return early with just the time series and 3D plots
        
        # Combined altitude vs sensor subplot
        fig_alt = make_subplots(rows=3, cols=1,
                               subplot_titles=('CO vs Altitude',
                                             'H2 vs Altitude',
                                             'Dust vs Altitude'))

        fig_alt.add_trace(go.Scatter(x=merged_df['altitude'], y=merged_df['CO'],
                                    mode='markers+lines', name='CO'), row=1, col=1)
        fig_alt.add_trace(go.Scatter(x=merged_df['altitude'], y=merged_df['H2'],
                                    mode='markers+lines', name='H2'), row=2, col=1)
        fig_alt.add_trace(go.Scatter(x=merged_df['altitude'], y=merged_df['Dust'],
                                    mode='markers+lines', name='Dust'), row=3, col=1)

        fig_alt.update_layout(height=900,
                             title_text="Sensor Readings vs Altitude",
                             showlegend=True)
        graphs['altitude_sensor'] = pio.to_json(fig_alt)

        # Individual altitude vs sensor graphs
        for sensor in ['CO', 'H2', 'Dust']:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=merged_df['altitude'], 
                                    y=merged_df[sensor],
                                    mode='markers+lines', 
                                    name=sensor))
            
            fig.update_layout(
                title=f"{sensor} Concentration vs Altitude",
                xaxis_title="Altitude (m)",
                yaxis_title=f"{sensor} {'(ppm)' if sensor in ['CO', 'H2'] else '(µg/m³)'}"
            )
            graphs[f'{sensor.lower()}_vs_altitude'] = pio.to_json(fig)

    except Exception as e:
        print(f"Error in create_detailed_graphs: {str(e)}")
        return jsonify({'error': f"Graph creation error: {str(e)}"}), 500

    return graphs

def calculate_sensor_errors(temperature, humidity):
    # Reference values
    T_ref_mq7_mq8 = 25  # °C
    T_ref_dust = 25     # °C
    H_ref_mq7 = 70      # %
    H_ref_mq8 = 70    # %
    H_ref_dust = 70     # %
    
    # Temperature and humidity as floats
    T = float(temperature)
    H = float(humidity)
    
    # Calculate errors for each sensor
    # MQ7 (CO Sensor)
    mq7_error = abs(0.01 * (T - T_ref_mq7_mq8) + 0.02 * (H - H_ref_mq7)) * 100
    
    # MQ8 (H2 Sensor)
    mq8_error = abs(0.015 * (T - T_ref_mq7_mq8) + 0.025 * (H - H_ref_mq8)) * 100
    
    # Dust Sensor
    dust_error = abs(0.005 * (T - T_ref_dust) + 0.03 * (H - H_ref_dust)) * 100
    
    return {
        'CO': round(mq7_error, 2),
        'H2': round(mq8_error, 2),
        'Dust': round(dust_error, 2)
    }

@app.route('/upload', methods=['POST'])
def upload_file():
    global graphs, warning_message
    try:
        print("Starting file upload process...")
        
        if 'file' not in request.files:
            print("No file part in request")  # Debug print
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("No selected file")  # Debug print
            return jsonify({'error': 'No selected file'}), 400
        
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        
        print(f"Temperature: {temperature}, Humidity: {humidity}")  # Debug print
        
        # Calculate sensor errors
        errors = calculate_sensor_errors(temperature, humidity)
        warning_message = (
            f"Environmental Condition Effects on Sensor Accuracy:\n"
            f"• CO Sensor: ±{errors['CO']}% error\n"
            f"• H2 Sensor: ±{errors['H2']}% error\n"
            f"• Dust Sensor: ±{errors['Dust']}% error\n"
            f"(at Temperature: {temperature}°C, Humidity: {humidity}%)"
        )
        
        # Read file content
        file_content = file.read().decode('utf-8')
        print("File content read successfully")  # Debug print
        
        # Parse data
        try:
            df = parse_data(file_content, temperature, humidity)
            print("Data parsed successfully")  # Debug print
        except Exception as e:
            print(f"Error in parse_data: {str(e)}")
            return jsonify({'error': f"Data parsing error: {str(e)}"}), 500
        
        # Create graphs
        try:
            graphs = create_detailed_graphs(df)
            print("Graphs created successfully")  # Debug print
        except Exception as e:
            print(f"Error in create_detailed_graphs: {str(e)}")
            return jsonify({'error': f"Graph creation error: {str(e)}"}), 500
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        print(f"Unexpected error in upload_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/result')
def result_page():
    return render_template('result.html', warning=warning_message)

@app.route('/get_graphs')
def get_graphs():
    global graphs
    return jsonify(graphs)

@app.route('/')
def home():
    return render_template('index.html')  # Assuming you have an index.html file

if __name__ == '__main__':
    app.run(debug=True)