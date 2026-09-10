import 'dart:convert';

import '../../../core/network/api_client.dart';

class SalesOrderLine {
  SalesOrderLine({
    required this.lineNo,
    required this.description,
    required this.qty,
    required this.lineTotal,
  });

  final int lineNo;
  final String description;
  final String qty;
  final String lineTotal;

  factory SalesOrderLine.fromJson(Map<String, dynamic> json) => SalesOrderLine(
        lineNo: json['line_no'] as int,
        description: json['description'] as String,
        qty: '${json['qty']}',
        lineTotal: '${json['line_total']}',
      );
}

class SalesOrder {
  SalesOrder({
    required this.salesOrderId,
    required this.soNumber,
    required this.quotationId,
    required this.status,
    required this.currencyCode,
    required this.grandTotal,
    required this.createdOn,
    this.opportunityId,
    this.customerId,
    this.opportunityName,
    this.customerName,
    this.lines = const [],
    this.workOrders = const [],
    this.paymentStubs = const [],
  });

  final String salesOrderId;
  final String soNumber;
  final String quotationId;
  final String? opportunityId;
  final String? customerId;
  final String? opportunityName;
  final String? customerName;
  final String status;
  final String currencyCode;
  final String grandTotal;
  final String createdOn;
  final List<SalesOrderLine> lines;
  final List<LinkedWorkOrder> workOrders;
  final List<PaymentStub> paymentStubs;

  factory SalesOrder.fromJson(Map<String, dynamic> json) => SalesOrder(
        salesOrderId: json['sales_order_id'] as String,
        soNumber: json['so_number'] as String,
        quotationId: json['quotation_id'] as String,
        opportunityId: json['opportunity_id'] as String?,
        customerId: json['customer_id'] as String?,
        opportunityName: json['opportunity_name'] as String?,
        customerName: json['customer_name'] as String?,
        status: json['status'] as String,
        currencyCode: json['currency_code'] as String,
        grandTotal: '${json['grand_total']}',
        createdOn: '${json['created_on']}',
        lines: (json['lines'] as List<dynamic>?)
                ?.map((e) => SalesOrderLine.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
        workOrders: (json['work_orders'] as List<dynamic>?)
                ?.map((e) => LinkedWorkOrder.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
        paymentStubs: (json['payment_stubs'] as List<dynamic>?)
                ?.map((e) => PaymentStub.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );
}

class LinkedWorkOrder {
  LinkedWorkOrder({
    required this.workOrderId,
    required this.woNumber,
    required this.status,
  });

  final String workOrderId;
  final String woNumber;
  final String status;

  factory LinkedWorkOrder.fromJson(Map<String, dynamic> json) => LinkedWorkOrder(
        workOrderId: json['work_order_id'] as String,
        woNumber: json['wo_number'] as String,
        status: json['status'] as String,
      );
}

class PaymentStub {
  PaymentStub({
    required this.paymentStubId,
    required this.paymentStatus,
    required this.amount,
    required this.currencyCode,
    required this.recordedOn,
    this.paymentReceiptId,
    this.receiptNumber,
  });

  final String paymentStubId;
  final String paymentStatus;
  final String amount;
  final String currencyCode;
  final String recordedOn;
  final String? paymentReceiptId;
  final String? receiptNumber;

  factory PaymentStub.fromJson(Map<String, dynamic> json) => PaymentStub(
        paymentStubId: json['payment_stub_id'] as String,
        paymentStatus: json['payment_status'] as String,
        amount: '${json['amount']}',
        currencyCode: json['currency_code'] as String,
        recordedOn: '${json['recorded_on']}',
        paymentReceiptId: json['payment_receipt_id'] as String?,
        receiptNumber: json['receipt_number'] as String?,
      );
}

class SalesOrderListResult {
  SalesOrderListResult({required this.items, required this.total});

  final List<SalesOrder> items;
  final int total;

  factory SalesOrderListResult.fromJson(Map<String, dynamic> json) =>
      SalesOrderListResult(
        items: (json['items'] as List<dynamic>)
            .map((e) => SalesOrder.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int,
      );
}

class SalesOrderService {
  SalesOrderService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<SalesOrderListResult> list({
    int page = 1,
    String? status,
    String? opportunityId,
    String? customerId,
  }) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '25',
      if (status != null && status.isNotEmpty) 'status': status,
      if (opportunityId != null && opportunityId.isNotEmpty) 'opportunity_id': opportunityId,
      if (customerId != null && customerId.isNotEmpty) 'customer_id': customerId,
    };
    final response = await _client.get('/api/v1/sal/sales-orders', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load sales orders (${response.statusCode})',
      );
    }
    return SalesOrderListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<SalesOrder> getById(String id) async {
    final response = await _client.get('/api/v1/sal/sales-orders/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load sales order (${response.statusCode})',
      );
    }
    return SalesOrder.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<String> confirm(String id) async {
    final response = await _client.post('/api/v1/sal/sales-orders/$id/confirm');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to confirm sales order (${response.statusCode})',
      );
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['message'] as String? ?? 'Sales order confirmed';
  }

  Future<String> recordPaymentStub(String id) async {
    final response = await _client.post('/api/v1/sal/sales-orders/$id/record-payment-stub');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to record payment stub (${response.statusCode})',
      );
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['message'] as String? ?? 'Payment stub recorded';
  }

  Future<String> generateInvoiceStub(String id) async {
    final response = await _client.post('/api/v1/sal/sales-orders/$id/generate-invoice-stub');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to generate invoice (${response.statusCode})',
      );
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['message'] as String? ?? 'Invoice created';
  }
}
