import ROOT

categories=['res2b', 'res1b', 'boosted']
channels=['tauTau', 'muTau', 'eTau']

process_to_remove = []

for channel in channels:
    for category in categories:
        f = ROOT.TFile.Open(f"/eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/hh_{category}_{channel}_2022_13p6TeV.input.root", "READ")
        for key in f.GetListOfKeys():
            hist = key.ReadObj()
            if hist.InheritsFrom("TH1"):
                if hist.Integral() <= 0:
                    process_to_remove.append(hist.GetName())
                    # print(process_to_remove)
            else:
                continue
        if process_to_remove is not []:
            print(f"file: hh_{category}_{channel}_2022_13p6TeV.input.root")
            print(f"Process to remove: {process_to_remove}")    
            # python3 remove_processes.py /eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/hh_{category}_{channel}_2022_13p6TeV.txt $process_to_remove -d /eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/
            # mv /eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/hh_{category}_{channel}_2022_13p6TeV_1.txt /eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/hh_{category}_{channel}_2022_13p6TeV.txt
        else:
            print("No process found with negative or zero integral.")
        f.Close()
        process_to_remove = []