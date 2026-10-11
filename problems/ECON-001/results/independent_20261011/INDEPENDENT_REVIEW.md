獨立審查者：/root/independent_review；本次為靜態與產物審查，未重跑科學計算。

兩項 raw stdout 解析後等同 result.json，20/22 個 execution input SHA256 仍吻合；各 pinned source head 之外僅新增本輪 experiment/result/round，舊 tracked artifacts 無變動。

CHEM：642 筆，513/129 切分，GAFF MAE1.114、mean MAE3.120/RMSE4.382；12 poison IDs、8 hit、4 miss、C5=false；9 個固定具名控制均拒絕，uncertainty 同時縮放的真正計算變體為3 hits。C2_net_charge_clean NOT_RUN；C4_scaffold_split_degrades INHERITED_FAIL_NOT_RUN；exit1 保留科學門檻 FAIL。

ECON：正常三方接受；12 個負向控制為 author=true、Fraction=false、existing=false。13 個子程序 execution 逐一吻合 matrix，argv[3] 均指向實際具名突變；12 份負例 stderr 均於 endpoint equality assert 以 AssertionError 結束，屬預期拒絕，沒有用基礎設施失敗冒充拒絕。第一個固定排序案例5.70→5.69確認原 verify 合約漏檢，不能當成 survey 或因果反例。

兩項 mask1、USD0、執行不重疊、無 timeout，均在19:17:09UTC前结束。Python real-location warning確實存在，包括13個子程序，並已保留；不得稱stderr為空。第二次科學重現 NOT_RUN。
