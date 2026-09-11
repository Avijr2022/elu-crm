import 'dart:convert';

import '../../../core/network/api_client.dart';

class Invoice {
  Invoice({
    required this.invoiceId,
    required this.invoiceNumber,
    required this.status,
    required this.invoiceDate,
    required this.currencyCode,
    required this.subtotal,
    required this.taxTotal,
    required this.grandTotal,
    required this.allocatedTotal,
    required this.balanceDue,
    required this.createdOn,
    this.customerId,
    this.customerName,
    this.salesOrderId,
    this.soNumber,
    this.issuedOn,
    this.allocations = const [],
  });

  final String invoiceId;
  final String invoiceNumber;
  final String? customerId;
  final String? customerName;
  final String? salesOrderId;
  final String? soNumber;
  final String status;
  final String invoiceDate;
  final String currencyCode;
  final String subtotal;
  final String taxTotal;
  final String grandTotal;
  final String allocatedTotal;
  final String balanceDue;
  final String? issuedOn;
  final String createdOn;
  final List<InvoiceAllocation> allocations;

  bool get isDraft => status == 'DRAFT';
  bool get isIssued => status == 'ISSUED';

  factory Invoice.fromJson(Map<String, dynamic> json) => Invoice(
        invoiceId: json['invoice_id'] as String,
        invoiceNumber: json['invoice_number'] as String,
        customerId: json['customer_id'] as String?,
        customerName: json['customer_name'] as String?,
        salesOrderId: json['sales_order_id'] as String?,
        soNumber: json['so_number'] as String?,
        status: json['status'] as String,
        invoiceDate: '${json['invoice_date']}',
        currencyCode: json['currency_code'] as String,
        subtotal: '${json['subtotal']}',
        taxTotal: '${json['tax_total']}',
        grandTotal: '${json['grand_total']}',
        allocatedTotal: '${json['allocated_total'] ?? '0'}',
        balanceDue: '${json['balance_due'] ?? '0'}',
        issuedOn: json['issued_on'] as String?,
        createdOn: '${json['created_on']}',
        allocations: (json['allocations'] as List<dynamic>?)
                ?.map((e) =>
                    InvoiceAllocation.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );
}

class InvoiceAllocation {
  InvoiceAllocation({
    required this.paymentAllocationId,
    required this.paymentReceiptId,
    required this.allocatedAmount,
    this.receiptNumber,
  });

  final String paymentAllocationId;
  final String paymentReceiptId;
  final String? receiptNumber;
  final String allocatedAmount;

  factory InvoiceAllocation.fromJson(Map<String, dynamic> json) =>
      InvoiceAllocation(
        paymentAllocationId: json['payment_allocation_id'] as String,
        paymentReceiptId: json['payment_receipt_id'] as String,
        receiptNumber: json['receipt_number'] as String?,
        allocatedAmount: '${json['allocated_amount']}',
      );
}

class InvoiceListResult {
  InvoiceListResult({required this.items, required this.total});

  final List<Invoice> items;
  final int total;

  factory InvoiceListResult.fromJson(Map<String, dynamic> json) =>
      InvoiceListResult(
        items: (json['items'] as List<dynamic>)
            .map((e) => Invoice.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int,
      );
}

class InvoiceService {
  InvoiceService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<InvoiceListResult> list({int page = 1, String? status}) async {
    final query = <String, String>{'page': '$page', 'page_size': '25'};
    if (status != null && status.isNotEmpty) query['status'] = status;
    final response = await _client.get('/api/v1/fin/invoices', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load invoices (${response.statusCode})',
      );
    }
    return InvoiceListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Invoice> getById(String id) async {
    final response = await _client.get('/api/v1/fin/invoices/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load invoice (${response.statusCode})',
      );
    }
    return Invoice.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  /// Issues a DRAFT invoice (DRAFT → ISSUED). Returns the updated invoice.
  Future<Invoice> issue(String id) async {
    final response = await _client.post('/api/v1/fin/invoices/$id/issue');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to issue invoice (${response.statusCode})',
      );
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return Invoice.fromJson(body['invoice'] as Map<String, dynamic>);
  }
}
