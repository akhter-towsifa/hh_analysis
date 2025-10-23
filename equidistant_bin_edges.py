import ROOT, array, math

def transform_binning(hist, binning, custom_bin_edges):
    def clone_hist(*args, **kwargs):
        clone = hist.__class__(
            hist.GetName()+'_clone',
            ";".join([hist.GetTitle(), hist.GetXaxis().GetTitle(), hist.GetYaxis().GetTitle()]),
            *args,
            **kwargs
        )
        clone.Sumw2()
        return clone

    if binning == "numbers":
        n_bins = hist.GetNbinsX()
        x_min = 0
        x_max = n_bins + x_min
        clone = clone_hist(n_bins, x_min, x_max)

        for b in range(1, n_bins + 1):
            clone.SetBinContent(b, hist.GetBinContent(b))
            clone.SetBinError(b, hist.GetBinError(b))
        for b in range(0, n_bins+1):
            clone.GetXaxis().ChangeLabel(b+1, labText=f"{custom_bin_edges[b]}")

        clone.GetXaxis().SetNdivisions(len(custom_bin_edges), 2, 2)

    elif binning == "numbers_width":
        n_bins = hist.GetNbinsX()
        x_min = 0.5
        x_max = n_bins + 0.5
        clone = clone_hist(n_bins, x_min, x_max)

        for b in range(1, n_bins + 1):
            clone.SetBinContent(b, hist.GetBinContent(b) / hist.GetBinWidth(b))
            clone.SetBinError(b, hist.GetBinError(b) / hist.GetBinWidth(b))

    return clone

shape_file = ROOT.TFile('/eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/hh_res2b_tauTau_2022_13p6TeV.input.root', "READ")
output_rebinned_file = ROOT.TFile("/eos/user/t/toakhter/bin_opt_tests/bin_opt_test_oct_hamburg_v2/equal_integral/equal_integral_binning_22preEE_tautau_res2b__hooks_qcd_test1.root", "RECREATE")
out_dir = output_rebinned_file.mkdir("cat_22preEE_tautau_res2b")

for key in shape_file.GetListOfKeys():
    hist = key.ReadObj()

    if hist.InheritsFrom("TH1"):
        rebinned = ROOT.TH1D(hist.GetName(), hist.GetTitle(), len(custom_edges)-1, custom_edges)
        rebinned_equidistant = transform_binning(rebinned, "numbers", custom_edges)

    else:
        continue

    out_dir.cd()
    rebinned_equidistant.Write()
    rebinned.Reset()
    rebinned_equidistant.Reset()


output_rebinned_file.Close()
shape_file.Close()

print(f"Rebinned histograms are saved to {output_rebinned_file}")
