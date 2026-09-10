import 'package:flutter/foundation.dart';

import '../../features/platform/data/edition_service.dart';
import 'crm_features.dart';

class EditionController extends ChangeNotifier {
  EditionController({EditionService? service})
      : _service = service ?? EditionService();

  final EditionService _service;
  final Set<String> _enabled = {};
  bool loaded = false;
  bool loading = false;

  bool has(String code) => _enabled.contains(code);
  bool get hasLead => has(CrmFeatures.lead);
  bool get hasOpportunity => has(CrmFeatures.opportunity);
  bool get hasCustomer => has(CrmFeatures.customer);
  bool get hasActivity => has(CrmFeatures.activity);
  bool get hasSalQuote => has(CrmFeatures.salQuote);
  bool get hasPrjWo => has(CrmFeatures.prjWo);
  bool get hasFinInvoice => has(CrmFeatures.finInvoice);

  Future<void> load() async {
    if (loading) return;
    loading = true;
    var ok = false;
    try {
      final e = await _service.tenantEdition();
      _enabled
        ..clear()
        ..addAll(
          e.features
              .where((f) => f['is_enabled'] == true)
              .map((f) => f['feature_code'] as String),
        );
      ok = true;
    } catch (e) {
      if (kDebugMode) debugPrint('Edition load failed: $e');
      _enabled.clear();
    } finally {
      loading = false;
      loaded = ok;
      notifyListeners();
    }
  }

  void clear() {
    _enabled.clear();
    loaded = false;
    notifyListeners();
  }
}
