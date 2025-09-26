import ROOT, array, math
import numpy as np

# #the rename_processes tool did not copy "data_obs" histogram, so copying it manually here
# f = ROOT.TFile.Open("renamed_datacard_shapes/shapes__cat_22preEE_tautau_res2b__hooks_qcd.root", "UPDATE")
# f.cd("cat_22preEE_tautau_res2b")
# # if not ROOT.gDirectory.GetListOfKeys().Contains("data_obs"):
# hist_copy = ROOT.gDirectory.Get("data_obs")
# f.cd()
# hist_copy.Write()
# f.Close()


shape_file = ROOT.TFile('renamed_datacard_shapes/shapes__cat_22preEE_tautau_res2b__hooks_qcd.root', "READ")
output_rebinned_file = ROOT.TFile("renamed_datacard_shapes/equal_integral_binning_22preEE_tautau_res2b__hooks_qcd.root", "RECREATE")
out_dir = output_rebinned_file.mkdir("cat_22preEE_tautau_res2b")

signal_names = ["ggHH_kl_1_kt_1_hbbhtt"]#, "ggHH_kl_2p45_kt_1_hbbhtt", "ggHH_kl_5_kt_1_hbbhtt"]
fixed_nbins = 7 #picking a fixed number of bins for all histograms

##### Rebinning with equal integral

# combinined signal histograms to determine bin edges with equal integrals
def compute_equal_integral_bin_edges(signal_hist_bin_edges, signal_hist_bin_contents, new_nbins):
    total_integral = np.sum(signal_hist_bin_contents)
    
    event_content_per_bin = total_integral / new_nbins
    print(f'total integral: {total_integral}, event content per bin: {event_content_per_bin}')

    ###new attempt 
    # bin_int = 0.0
    # bin_edge = [0.0]
    # indices_in_old_hist = [0]
    # for idx,i in enumerate(signal_hist_bin_contents):
    #     bin_int += i
    #     if bin_int >= event_content_per_bin: # 0.02812474982968319
    #         print(f'idx: {idx}, bin_int: {bin_int}, signal_hist_bin_edges[idx+1]: {signal_hist_bin_edges[idx+1]}')
    #         bin_edge.append(signal_hist_bin_edges[idx+1])
    #         indices_in_old_hist.append(idx+1)
    #         bin_int = 0.0
    #     continue
    

    ###old attempt



    # print(f'total integral: {total_integral}, event content per bin: {event_content_per_bin}')
    bin_wise_integral = np.cumsum(signal_hist_bin_contents) #this is an array where each element is the integral up to that bin
    # print(f'bin_wise_integral: {bin_wise_integral}')

    new_bin_edges = [signal_hist_bin_edges[0]]
    new_bin_edges_indices_in_old_hist = [0]

    for i in range(1, new_nbins):
        target_integral = i * event_content_per_bin
        # print(f'target_integral for bin {i}: {target_integral}')
        bin_index_target_integral = np.searchsorted(bin_wise_integral, target_integral) #find the index of the bin where the target integral is reached
        # print(f'bin_index_target_integral for bin {i}: {bin_index_target_integral}')

        new_bin_edge = signal_hist_bin_edges[bin_index_target_integral] #integral_before + fraction_inside_bin * (integral_in_bin - integral_before)
        new_bin_edges.append(new_bin_edge)
        new_bin_edges_indices_in_old_hist.append(bin_index_target_integral)

        # print(f'new_bin_edges[{i}]: {new_bin_edges[i]}')
    new_bin_edges.append(signal_hist_bin_edges[-1])
    new_bin_edges_indices_in_old_hist.append(len(signal_hist_bin_edges)-1)

    # for i in new_bin_edges_indices_in_old_hist:
    #     if i!=1:
    #         print("test i",i,np.sum(signal_hist_bin_contents[i:i+1]))

    return np.array(new_bin_edges), np.array(new_bin_edges_indices_in_old_hist)

def integrate_bins(hist, start, end):
    error = array.array('d', [0])
    int_values = hist.IntegralAndError(int(start)+1, int(end), error)
    int_errors = error[0]
    print(f'start {start} end {end} integrated int_values: {int_values}, int_errors: {int_errors}')
    return int_values, int_errors

def rebinAndFill(old_hist, new_bin_edges, new_bin_edges_indices_in_old_hist):
    new_hist = ROOT.TH1D(old_hist.GetName(), old_hist.GetTitle(), len(new_bin_edges)-1, new_bin_edges)

    for i in range(1, new_hist.GetNbinsX()+1):
        integral_bin_content, integral_bin_error = integrate_bins(old_hist, new_bin_edges_indices_in_old_hist[i-1], new_bin_edges_indices_in_old_hist[i]-1)
        new_hist.SetBinContent(i, integral_bin_content)
        new_hist.SetBinError(i, integral_bin_error)
        print(f'new_hist bin {i}, content: {new_hist.GetBinContent(i)}, error: {new_hist.GetBinError(i)}')

    return new_hist

def th1ToNumpy(histogram):
    nbins = histogram.GetNbinsX()
    # print(f'histogram.GetXaxis().GetBinLowEdge(1) {histogram.GetXaxis().GetBinLowEdge(1)} histogram.GetXaxis().GetBinUpEdge(nbins) {histogram.GetXaxis().GetBinUpEdge(nbins)}')
    bin_edges = np.array([histogram.GetXaxis().GetBinLowEdge(i) for i in range(1, nbins+2)])
    # print(f'nbins: {nbins}, bin_edges: {bin_edges}')
    bin_contents = np.array([histogram.GetBinContent(i) for i in range(1, nbins+1)])
    # print(f'bin_contents: {bin_contents}')
    bin_errors = np.array([histogram.GetBinError(i) for i in range(1, nbins+1)])
    # print(f'bin_errors: {bin_errors}')

    return bin_edges, bin_contents, bin_errors

def main():
    h_combined_signal = ROOT.TH1D("h_combined_signal", "h_combined_signal", shape_file.Get(signal_names[0]).GetNbinsX(), shape_file.Get(signal_names[0]).GetXaxis().GetXmin(), shape_file.Get(signal_names[0]).GetXaxis().GetXmax())
    h_combined_signal.Reset()

    for signal_name in signal_names:
        h = shape_file.Get(signal_name)
        h_combined_signal.Add(h)

    old_signal_bin_edges, old_signal_bin_values, old_signal_bin_errors = th1ToNumpy(h_combined_signal)
    new_signal_bin_edges, new_signal_bin_edges_indices_in_old_hist = compute_equal_integral_bin_edges(old_signal_bin_edges, old_signal_bin_values, fixed_nbins)

    print(f'new bin edges: {new_signal_bin_edges}, new_signal_bin_edges_indices_in_old_hist: {new_signal_bin_edges_indices_in_old_hist} ')
    print(new_signal_bin_edges[3], new_signal_bin_edges_indices_in_old_hist[3])

     # Rebin and save all histograms
    for key in shape_file.GetListOfKeys():
        print("key.GetName()", key.GetName())
        hist = key.ReadObj()

        if hist.InheritsFrom("TH1"):
            rebinned = rebinAndFill(hist, new_signal_bin_edges, new_signal_bin_edges_indices_in_old_hist)

        else:
            continue

        out_dir.cd()

        rebinned.Write()
    
    output_rebinned_file.Close()
    shape_file.Close()

if __name__ == "__main__":
    main()
    print(f"Rebinned histograms are saved to {output_rebinned_file}")
