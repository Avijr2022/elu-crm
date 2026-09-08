import 'package:elinkup_app/features/crm/presentation/l2c_demo_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  test('L2cDemoStorage saves and loads session per tenant', () async {
    SharedPreferences.setMockInitialValues({});
    await L2cDemoStorage.save(
      tenantCode: 'EIIP001',
      leadId: 'lead-1',
      opportunityId: 'opp-1',
      customerId: 'cust-1',
      completedSteps: {0, 2},
      hasOpportunityEdition: true,
    );
    final loaded = await L2cDemoStorage.load('EIIP001');
    expect(loaded, isNotNull);
    expect(loaded!.leadId, 'lead-1');
    expect(loaded.opportunityId, 'opp-1');
    expect(loaded.completedSteps, {0, 2});

    expect(await L2cDemoStorage.load('COMU001'), isNull);

    await L2cDemoStorage.clear('EIIP001');
    expect(await L2cDemoStorage.load('EIIP001'), isNull);
  });
}
