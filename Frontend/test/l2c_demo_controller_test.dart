import 'package:elinkup_app/features/crm/presentation/l2c_demo_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('buildUatReport includes edition, IDs, and step status', () {
    final controller = L2cDemoController(hasOpportunityEdition: true);
    controller.setLeadId('lead-abc');
    controller.setOpportunityId('opp-xyz');
    controller.toggleStep(0);
    controller.toggleStep(1);

    final report = controller.buildUatReport(
      tenantCode: 'EIIP001',
      tenantName: 'Euphoria Infotech',
      testerName: 'Demo User',
    );

    expect(report, contains('TC-L2C-CRM-01'));
    expect(report, contains('Edition: Professional'));
    expect(report, contains('EIIP001'));
    expect(report, contains('lead-abc'));
    expect(report, contains('opp-xyz'));
    expect(report, contains('[PASS] 1. Create lead'));
    expect(report, contains('[PASS] 2. Qualify lead'));
    expect(report, contains('[    ] 3. Convert to opportunity'));
    expect(report, contains('IN PROGRESS'));
  });

  test('buildUatReport sal scope includes quotation and sales order', () {
    final controller = L2cDemoController(
      hasOpportunityEdition: true,
      hasSalQuote: true,
    );
    final report = controller.buildUatReport(tenantCode: 'EIIP001');
    expect(report, contains('CRM + SAL quotation/SO confirm slice'));
    expect(report, contains('Convert to sales order'));
  });

  test('buildUatReport community edition omits opportunity', () {
    final controller = L2cDemoController(hasOpportunityEdition: false);
    controller.setLeadId('lead-1');
    controller.toggleStep(0);

    final report = controller.buildUatReport(tenantCode: 'COMU001');

    expect(report, contains('Edition: Community'));
    expect(report, contains('Convert to customer'));
    expect(report, isNot(contains('Opportunity:')));
  });
}
