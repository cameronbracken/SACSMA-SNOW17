import glob
from pathlib import Path
import pandas as pd


def load_sacsma_parameters(data_dir: str, forcing_type: str, gauge_id: str):

  # Construct file name from pieces
  filename = glob.glob(f'{data_dir}/model_output/{forcing_type}/**/{gauge_id}_*_model_parameters.txt')[0]

  # Load a dictionary of parameter values
  parameters = {}
  with open(filename) as f:
    for line in f:
      (key, val) = line.split()
      parameters[key] = val

  # Convert to dataframe
  # parameters_df = pd.Series(parameters).to_frame

  return parameters


def load_basin_attributes(data_dir: str, gauge_id: str):

  # Add the attributes path extention
  attributes_dir = Path(data_dir) / 'camels_attributes_v2.0' 

  # Check for existence
  if not attributes_dir.exists():
    raise RuntimeError(f"Attribute folder not found at {attributes_dir}")

  # Grab all attributes files
  txt_files = attributes_dir.glob('camels_*.txt')

  # Read-in attributes into one big dataframe
  dfs = []
  for txt_file in txt_files:
    df_temp = pd.read_csv(txt_file, sep=';', header=0, dtype={'gauge_id': str})
    df_temp = df_temp.set_index('gauge_id')
    dfs.append(df_temp)

  df = pd.concat(dfs, axis=1)

  # convert huc column to double digit strings
  df['huc'] = df['huc_02'].apply(lambda x: str(x).zfill(2))
  df = df.drop('huc_02', axis=1)

  # Choose only the basin we want
  attributes = df.loc[gauge_id]

  return attributes


def load_forcings(data_dir: str, forcing_type: str, gauge_id: str):
    
  # Grab the correct forcing file
  forcing_files = glob.glob(f'{data_dir}/basin_dataset_public_v1p2/basin_mean_forcing/{forcing_type}/**/{gauge_id}_*_forcing_leap.txt')
  assert len(forcing_files) == 1
  forcing_file = forcing_files[0]

  # Grab the data
  forcings = pd.read_csv(forcing_file, sep='\s+', header=3)

  # Datetime index
  forcings['Date'] = pd.to_datetime(forcings['Year'] * 10000 + forcings['Mnth'] * 100 + forcings['Day'], format='%Y%m%d')
#   forcings = forcings.set_index('Date')

  return forcings


def load_discharge(data_dir: str, forcing_type: str, gauge_id: str):
    
  # Grab the correct forcing file
  filename = glob.glob(f'{data_dir}/model_output/{forcing_type}/**/{gauge_id}_*_model_output.txt')[0]

  # Grab the data
  output = pd.read_csv(filename, sep='\s+')

  # Datetime index
  output['Date'] = pd.to_datetime(output['YR'] * 10000 + output['MNTH'] * 100 + output['DY'], format='%Y%m%d')
#   output = output.set_index('Date')

  return output