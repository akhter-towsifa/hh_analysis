import ROOT, array, math

f = ROOT.TFile.Open("/eos/user/t/toakhter/bin_opt_tests_sept17_hamburg/renamed_datacard_shapes/shapes__cat_22preEE_tautau_res2b__hooks_qcd.root", "UPDATE")
f.cd("cat_22preEE_tautau_res2b")
# if not ROOT.gDirectory.GetListOfKeys().Contains("data_obs"):
hist_copy = ROOT.gDirectory.Get("data_obs")
f.cd()
hist_copy.Write()
f.Close()




# shape_file = ROOT.TFile('./datacard/hh_res2b_tauTau_2018_13TeV.input.root', "READ")
shape_file = ROOT.TFile('/eos/user/t/toakhter/bin_opt_tests_sept17_hamburg/renamed_datacard_shapes/shapes__cat_22preEE_tautau_res2b__hooks_qcd.root', "READ")
# signal_branch = shape_file.Get("cat_22preEE_tautau_res2b/ggHH_kl_1_kt_1_22preEE_13p6TeV_hbbhtt")

# canvas = ROOT.TCanvas("c1", "c1", 1000, 1000, 1000, 750)
# canvas.SetGrid()

# bin_edges = array.array('d', [0.0, 0.553, 0.9512, 0.993, 0.9982000000000001, 0.9996, 1.0])

# rebinned_hist = ROOT.TH1D("h", "", len(bin_edges)-1 , bin_edges)

# for i in range(1, signal_branch.GetNbinsX()+1):
#     x = signal_branch.GetBinCenter(i)
#     y = signal_branch.GetBinContent(i)
#     rebinned_hist.Fill(x,y)

# rebinned_hist.Draw()

# canvas.SaveAs("/eos/user/t/toakhter/signal_binning_13_75.png")

##### Rebinning with equal integral

# output_rebinned_file = ROOT.TFile("/eos/user/t/toakhter/optimized_integral_binning_hh_res2b_tauTau_2018_13TeV.input.root", "RECREATE")
output_rebinned_file = ROOT.TFile("/eos/user/t/toakhter/bin_opt_tests_sept17_hamburg/renamed_datacard_shapes/equal_integral_binning_22preEE_tautau_res2b__hooks_qcd.root", "RECREATE")

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

        bin_content = hist.GetBinContent(j)
        bin_width = hist.GetBinWidth(j)
        loop_integral += bin_content
        # print(j, loop_integral)

        if loop_integral >= equal_integral_bin:
            edge = hist.GetXaxis().GetBinUpEdge(j)
            if edge > new_bin_edges[-1]:
                print(f'debug: edge {edge}')
                new_bin_edges.append(round(edge, 5))
            loop_integral = 0.0

        if len(new_bin_edges) - 1 == nbins:
            break

    if len(new_bin_edges) - 1 < nbins:
        if new_bin_edges[-1] < 1.0:
            new_bin_edges.append(1.0)

    return array.array('d', new_bin_edges)
        

fixed_nbins = 7 #len(bin_edges)-1

x_min = 0
x_max = 1

hist = shape_file.Get("ggHH_kl_1_kt_1_hbbhtt")
custom_edges = get_custom_edges_equal_integral(hist, fixed_nbins)
print(custom_edges)

# the rebinAndFill function is from StatInference common tools:
def rebinAndFill(new_hist, old_hist, epsilon=1e-7):
  def check_range(old_axis, new_axis):
    old_min = old_axis.GetBinLowEdge(1)
    old_max = old_axis.GetBinUpEdge(old_axis.GetNbins())
    new_min = new_axis.GetBinLowEdge(1)
    new_max = new_axis.GetBinUpEdge(new_axis.GetNbins())
    return old_min <= new_min and old_max >= new_max

  def get_new_bin(old_axis, new_axis, bin_id_old):
    old_low_edge = round(old_axis.GetBinLowEdge(bin_id_old), 4)
    old_up_edge = round(old_axis.GetBinUpEdge(bin_id_old), 4)
    bin_low_new = new_axis.FindFixBin(old_low_edge)
    bin_up_new = new_axis.FindFixBin(old_up_edge)

    new_up_edge = new_axis.GetBinUpEdge(bin_low_new)
    if not (bin_low_new == bin_up_new or \
            abs(old_up_edge - new_up_edge) <= epsilon * abs(old_up_edge + new_up_edge) * 2):
      old_bins = [ str(old_axis.GetBinLowEdge(n)) for n in range(1, old_axis.GetNbins() + 2)]
      new_bins = [ str(new_axis.GetBinLowEdge(n)) for n in range(1, new_axis.GetNbins() + 2)]
      print('old_bins: [{}]'.format(', '.join(old_bins)))
      print('new_bins: [{}]'.format(', '.join(new_bins)))

      raise RuntimeError("Incompatible bin edges")
    return bin_low_new

  def add_bin_content(bin_old, bin_new):
    cnt_old = old_hist.GetBinContent(bin_old)
    err_old = old_hist.GetBinError(bin_old)
    cnt_new = new_hist.GetBinContent(bin_new)
    err_new = new_hist.GetBinError(bin_new)
    cnt_upd = cnt_new + cnt_old
    err_upd = math.sqrt(err_new ** 2 + err_old ** 2)
    new_hist.SetBinContent(bin_new, cnt_upd)
    new_hist.SetBinError(bin_new, err_upd);

  n_dim = old_hist.GetDimension()
  if new_hist.GetDimension() != n_dim:
    raise RuntimeError("Incompatible number of dimensions")
  if n_dim < 1 or n_dim > 2:
    raise RuntimeError("Unsupported number of dimensions")

  if not check_range(old_hist.GetXaxis(), new_hist.GetXaxis()):
    raise RuntimeError("x ranges are not compatible")

  if n_dim > 1 and not check_range(old_hist.GetYaxis(), new_hist.GetYaxis()):
    raise RuntimeError("y ranges are not compatible")

  for x_bin_old in range(old_hist.GetNbinsX() + 2):
    x_bin_new = get_new_bin(old_hist.GetXaxis(), new_hist.GetXaxis(), x_bin_old)
    if n_dim == 1:
      add_bin_content(x_bin_old, x_bin_new)
    else:
      for y_bin_old in range(old_hist.GetNbinsY() + 2):
        y_bin_new = get_new_bin(old_hist.GetYaxis(), new_hist.GetYaxis(), y_bin_old)
        bin_old = old_hist.GetBin(x_bin_old, y_bin_old)
        bin_new = new_hist.GetBin(x_bin_new, y_bin_new)
        add_bin_content(bin_old, bin_new)



#hist_dir = shape_file.Get("cat_22preEE_tautau_res2b")
out_dir = output_rebinned_file.mkdir("cat_22preEE_tautau_res2b")

#for key in hist_dir.GetListOfKeys():
for key in shape_file.GetListOfKeys():
    print("key.GetName()", key.GetName())
    hist = key.ReadObj()

    if hist.InheritsFrom("TH1"):
        # print(custom_edges)
        # rebinned = hist.Rebin(fixed_nbins, hist.GetTitle(), array.array('d', [0.0, 0.416, 0.947, 0.99, 1.0]) )#custom_edges) #hist.GetName(), hist.GetTitle(), fixed_nbins, custom_edges)
        # rebinned = hist.Rebin(len(custom_edges)-1, hist.GetTitle(), custom_edges)#get_custom_edges_equal_integral(hist, fixed_nbins))
        rebinned = ROOT.TH1D(hist.GetName(), hist.GetTitle(), len(custom_edges)-1, custom_edges)
        rebinAndFill(rebinned, hist)

    else:
        continue

    out_dir.cd()
    # output_rebinned_file.cd()
    rebinned.Write()
    rebinned.Reset()


output_rebinned_file.Close()
shape_file.Close()

print(f"Rebinned histograms are saved to {output_rebinned_file}")
