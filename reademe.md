Set up .venv and install mokucli and moku python package and other python dependencies


moku_arbitrary_waveform_poc source .venv/bin/activate
(.venv) ➜  moku_arbitrary_waveform_poc pip install moku 


mokucli list         
                Name  Serial     HW     FW IPv4                 IPv6                                  
------------------------------------------------------------------------------------------------------
       MokuGo-003455    3455     Go    622 169.254.48.42        fe80::7269:79ff:feb9:35fc%13  

moku_arbitrary_waveform_poc mokucli feature install 169.254.48.42 api-server 
ℹ Feature 622/api-server not found locally. Attempting to download...
  Downloading api-server ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
✓ Downloaded api-server
✓ Uploaded 1/1 features
  Uploading 1 features to 169.254.48.42... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
! Please restart the Moku to complete the update process
(.venv) ➜  moku_arbitrary_waveform_poc 


moku.exceptions.NoInstrumentBitstream: Instrument files not available, please run `mokucli instrument download 4.0.3` to download latest instrument data

moku_arbitrary_waveform_poc mokucli instrument download 4.0.3 # this step can take a few minutes

