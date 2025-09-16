import ROOT, array

shape_file = ROOT.TFile('./datacard/hh_res2b_tauTau_2018_13TeV.input.root', "READ")
signal_branch = shape_file.Get("ggHH_kl_1_kt_1_hbbhtt")

canvas = ROOT.TCanvas("c1", "c1", 1000, 1000, 1000, 750)
canvas.SetGrid()

bin_edges = array.array('d', [0.0, 0.416, 0.947, 0.99, 1.0])

rebinned_hist = ROOT.TH1D("h", "", len(bin_edges)-1 , bin_edges)

for i in range(1, signal_branch.GetNbinsX()+1):
    x = signal_branch.GetBinCenter(i)
    y = signal_branch.GetBinContent(i)
    rebinned_hist.Fill(x,y)

rebinned_hist.Draw()

# canvas.SaveAs("signal_binning_13_75.png")

##### Rebinning with equal integral

output_rebinned_file = ROOT.TFile("optimized_integral_binning_hh_res2b_tauTau_2018_13TeV.input.root", "RECREATE")

def get_custom_edges_equal_integral(hist, nbins):
    """Compute bin edges where each bin has equal integral"""
    total_integral = hist.Integral()
    if total_integral == 0:
        return array.array('d', [hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()])

    equal_integral_bin = total_integral/nbins
    print(f'equal integral per bin: {equal_integral_bin}, histogram integral: {hist.Integral()}')

    new_bin_edges = [0.0] #adding the first edge on the low end of hist
    loop_integral = 0.0

    for j in range(1, hist.GetNbinsX()+1):
        # loop_integral += hist.GetBinContent(j)# * hist.GetBinWidth(j)

        bin_content = hist.GetBinContent(j)
        bin_width = hist.GetBinWidth(j)
        loop_integral += bin_content #* bin_width
        print(j, loop_integral)

        if loop_integral >= equal_integral_bin:
            edge = hist.GetXaxis().GetBinUpEdge(j)
            if edge > new_bin_edges[-1]:
                print(f'debug: edge {edge}')
                new_bin_edges.append(edge)
            loop_integral = 0.0

        if len(new_bin_edges) - 1 == nbins:
            break

    if len(new_bin_edges) - 1 < nbins:
        if new_bin_edges[-1] < 1.0:#hist.GetXaxis().GetXmax():
            new_bin_edges.append(1.0)#hist.GetXaxis().GetXmax())

    print(f"new bin edges {new_bin_edges}")
    return array.array('d', new_bin_edges)
        

fixed_nbins = len(bin_edges)-1

x_min = 0
x_max = 1

hist = shape_file.Get("ggHH_kl_1_kt_1_hbbhtt")

for key in shape_file.GetListOfKeys():
    hist = key.ReadObj()

    if hist.InheritsFrom("TH1"):
        # rebinned = hist.Rebin(fixed_nbins, hist.GetTitle(), array.array('d', [0.0, 0.416, 0.947, 0.99, 1.0]) )
        rebinned = hist.Rebin(fixed_nbins, hist.GetTitle(), get_custom_edges_equal_integral(hist, fixed_nbins))
    else:
        continue

    output_rebinned_file.cd()
    rebinned.Write()

output_rebinned_file.Close()
shape_file.Close()

print(f"Rebinned histograms are saved to {output_rebinned_file}")
