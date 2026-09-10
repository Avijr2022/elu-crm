import 'dart:convert';

import '../../../core/network/api_client.dart';

class PaymentReceipt {
  PaymentReceipt({
    required this.paymentReceiptId,
    required this.receiptNumber,
    required this.amount,
    required this.currencyCode,
    required this.receivedOn,
    required this.status,
    required this.method,
    this.customerId,
    this.customerName,
    this.salesOrderId,
    this.soNumber,
    this.allocations = const [],
  });

  final String paymentReceiptId;
  final String receiptNumber;
  final String? customerId;
  final String? customerName;
  final String? salesOrderId;
  final String? soNumber;
  final String amount;
  final String currencyCode;
  final String receivedOn;
  final String status;
  final String method;
  final List<PaymentAllocation> allocations;

  factory PaymentReceipt.fromJson(Map<String, dynamic> json) => PaymentReceipt(
        paymentReceiptId: json['payment_receipt_id'] as String,
        receiptNumber: json['receipt_number'] as String,
        customerId: json['customer_id'] as String?,
        customerName: json['customer_name'] as String?,
        salesOrderId: json['sales_order_id'] as String?,
        soNumber: json['so_number'] as String?,
        amount: '${json['amount']}',
        currencyCode: json['currency_code'] as String,
        receivedOn: '${json['received_on']}',
        status: json['status'] as String,
        method: json['method'] as String,
        allocations: (json['allocations'] as List<dynamic>?)
                ?.map((e) => PaymentAllocation.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );
}

class PaymentAllocation {
  PaymentAllocation({
    required this.paymentAllocationId,
    required this.allocatedAmount,
    required this.invoiceId,
  });

  final String paymentAllocationId;
  final String allocatedAmount;
  final String invoiceId;

  factory PaymentAllocation.fromJson(Map<String, dynamic> json) => PaymentAllocation(
        paymentAllocationId: json['payment_allocation_id'] as String,
        allocatedAmount: '${json['allocated_amount']}',
        invoiceId: json['invoice_id'] as String,
      );
}

class PaymentReceiptListResult {
  PaymentReceiptListResult({required this.items, required this.total});

  final List<PaymentReceipt> items;
  final int total;

  factory PaymentReceiptListResult.fromJson(Map<String, dynamic> json) =>
      PaymentReceiptListResult(
        items: (json['items'] as List<dynamic>)
            .map((e) => PaymentReceipt.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int,
      );
}

class PaymentReceiptService {
  PaymentReceiptService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<PaymentReceiptListResult> list({int page = 1}) async {
    final response = await _client.get(
      '/api/v1/fin/payment-receipts',
      query: {'page': '$page', 'page_size': '25'},
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load payment receipts (${response.statusCode})',
      );
    }
    return PaymentReceiptListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<PaymentReceipt> getById(String id) async {
    final response = await _client.get('/api/v1/fin/payment-receipts/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load payment receipt (${response.statusCode})',
      );
    }
    return PaymentReceipt.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
