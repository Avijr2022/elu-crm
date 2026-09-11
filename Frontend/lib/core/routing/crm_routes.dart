abstract final class CrmRoutes {
  static const login = '/login';
  static const home = '/';
  static const leads = '/crm/leads';
  static const leadsNew = '/crm/leads/new';
  static String leadDetail(String id) => '/crm/leads/$id';
  static String leadEdit(String id) => '/crm/leads/$id/edit';
  static const opportunities = '/crm/opportunities';
  static const opportunitiesNew = '/crm/opportunities/new';
  static const pipeline = '/crm/opportunities/pipeline';
  static String opportunityDetail(String id) => '/crm/opportunities/$id';
  static String opportunityEdit(String id) => '/crm/opportunities/$id/edit';
  static const customers = '/crm/customers';
  static const customersNew = '/crm/customers/new';
  static String customerDetail(String id) => '/crm/customers/$id';
  static const activityTimeline = '/crm/activities/timeline';
  static const opportunityStages = '/crm/settings/opportunity-stages';
  static const activityOutcomes = '/crm/settings/activity-outcomes';
  static const activityTypes = '/crm/settings/activity-types';
  static const l2cDemo = '/crm/demo/l2c';
  static const quotations = '/crm/quotations';
  static const quotationsNew = '/crm/quotations/new';
  static String quotationDetail(String id) => '/crm/quotations/$id';
  static const workOrders = '/crm/work-orders';
  static String workOrderDetail(String id) => '/crm/work-orders/$id';
  static const salesOrders = '/crm/sales-orders';
  static String salesOrderDetail(String id) => '/crm/sales-orders/$id';
  static String salesOrdersFiltered({
    String? opportunityId,
    String? customerId,
    String? status,
  }) {
    final q = <String, String>{};
    if (opportunityId != null && opportunityId.isNotEmpty) {
      q['opportunity_id'] = opportunityId;
    }
    if (customerId != null && customerId.isNotEmpty) {
      q['customer_id'] = customerId;
    }
    if (status != null && status.isNotEmpty) {
      q['status'] = status;
    }
    if (q.isEmpty) return salesOrders;
    return Uri(path: salesOrders, queryParameters: q).toString();
  }

  static const tenantBranding = '/settings/branding';
  static const paymentReceipts = '/crm/payment-receipts';
  static String paymentReceiptDetail(String id) => '/crm/payment-receipts/$id';
  static const invoices = '/crm/invoices';
  static String invoiceDetail(String id) => '/crm/invoices/$id';
  static const upgrade = '/upgrade';
}
