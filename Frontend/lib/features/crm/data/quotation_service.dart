import 'dart:convert';

import '../../../core/network/api_client.dart';

class QuotationLine {
  QuotationLine({
    required this.quotationLineId,
    required this.quotationId,
    required this.lineNo,
    required this.description,
    required this.qty,
    required this.unitPrice,
    required this.discountPct,
    required this.lineTotal,
    this.productCode,
    this.taxCode,
  });

  final String quotationLineId;
  final String quotationId;
  final int lineNo;
  final String? productCode;
  final String description;
  final String qty;
  final String unitPrice;
  final String discountPct;
  final String? taxCode;
  final String lineTotal;

  factory QuotationLine.fromJson(Map<String, dynamic> json) => QuotationLine(
        quotationLineId: json['quotation_line_id'] as String,
        quotationId: json['quotation_id'] as String,
        lineNo: json['line_no'] as int,
        productCode: json['product_code'] as String?,
        description: json['description'] as String,
        qty: '${json['qty']}',
        unitPrice: '${json['unit_price']}',
        discountPct: '${json['discount_pct']}',
        taxCode: json['tax_code'] as String?,
        lineTotal: '${json['line_total']}',
      );
}

class Quotation {
  Quotation({
    required this.quotationId,
    required this.quotationNumber,
    required this.status,
    required this.currencyCode,
    required this.subtotal,
    required this.discountTotal,
    required this.taxTotal,
    required this.grandTotal,
    this.customerId,
    this.opportunityId,
    this.salesOrderId,
    this.soNumber,
    this.lines = const [],
  });

  final String quotationId;
  final String quotationNumber;
  final String? customerId;
  final String? opportunityId;
  final String? salesOrderId;
  final String? soNumber;
  final String status;
  final String currencyCode;
  final String subtotal;
  final String discountTotal;
  final String taxTotal;
  final String grandTotal;
  final List<QuotationLine> lines;

  factory Quotation.fromJson(Map<String, dynamic> json) => Quotation(
        quotationId: json['quotation_id'] as String,
        quotationNumber: json['quotation_number'] as String,
        customerId: json['customer_id'] as String?,
        opportunityId: json['opportunity_id'] as String?,
        salesOrderId: json['sales_order_id'] as String?,
        soNumber: json['so_number'] as String?,
        status: json['status'] as String,
        currencyCode: json['currency_code'] as String,
        subtotal: '${json['subtotal']}',
        discountTotal: '${json['discount_total']}',
        taxTotal: '${json['tax_total']}',
        grandTotal: '${json['grand_total']}',
        lines: (json['lines'] as List<dynamic>?)
                ?.map((e) => QuotationLine.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      );
}

class QuotationListResult {
  QuotationListResult({required this.items, required this.total});

  final List<Quotation> items;
  final int total;

  factory QuotationListResult.fromJson(Map<String, dynamic> json) =>
      QuotationListResult(
        items: (json['items'] as List<dynamic>)
            .map((e) => Quotation.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int,
      );
}

class QuotationService {
  QuotationService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<QuotationListResult> list({int page = 1, String? status}) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '25',
      if (status != null && status.isNotEmpty) 'status': status,
    };
    final response = await _client.get('/api/v1/sal/quotations', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load quotations (${response.statusCode})',
      );
    }
    return QuotationListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Quotation> getById(String id) async {
    final response = await _client.get('/api/v1/sal/quotations/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load quotation (${response.statusCode})',
      );
    }
    return Quotation.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Quotation> updateStatus(String id, String status) async {
    final response = await _client.patch(
      '/api/v1/sal/quotations/$id/status',
      body: jsonEncode({'status': status}),
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to update status (${response.statusCode})',
      );
    }
    return Quotation.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Quotation> create({
    required String customerId,
    String currencyCode = 'INR',
    String? notes,
  }) async {
    final response = await _client.post(
      '/api/v1/sal/quotations',
      body: jsonEncode({
        'customer_id': customerId,
        'currency_code': currencyCode,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      }),
    );
    if (response.statusCode != 201) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to create quotation (${response.statusCode})',
      );
    }
    return Quotation.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<QuotationLine> addLine(
    String quotationId, {
    required String description,
    String qty = '1',
    String unitPrice = '0',
    String discountPct = '0',
    String taxCode = 'GST18',
  }) async {
    final response = await _client.post(
      '/api/v1/sal/quotations/$quotationId/lines',
      body: jsonEncode({
        'description': description,
        'qty': qty,
        'unit_price': unitPrice,
        'discount_pct': discountPct,
        'tax_code': taxCode,
      }),
    );
    if (response.statusCode != 201) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to add line (${response.statusCode})',
      );
    }
    return QuotationLine.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<Quotation> recordCustomerResponse(
    String id,
    String responseType, {
    String? comment,
  }) async {
    final response = await _client.post(
      '/api/v1/sal/quotations/$id/customer-response',
      body: jsonEncode({
        'response_type': responseType,
        if (comment != null && comment.isNotEmpty) 'comment': comment,
      }),
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to record response (${response.statusCode})',
      );
    }
    return Quotation.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<List<QuotationStatusEntry>> getHistory(String id) async {
    final response = await _client.get('/api/v1/sal/quotations/$id/history');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load history (${response.statusCode})',
      );
    }
    final list = jsonDecode(response.body) as List<dynamic>;
    return list
        .map((e) => QuotationStatusEntry.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<QuotationLine> updateLine(
    String quotationId,
    String lineId, {
    required String description,
    String qty = '1',
    String unitPrice = '0',
    String taxCode = 'GST18',
  }) async {
    final response = await _client.put(
      '/api/v1/sal/quotations/$quotationId/lines/$lineId',
      body: jsonEncode({
        'description': description,
        'qty': qty,
        'unit_price': unitPrice,
        'tax_code': taxCode,
      }),
    );
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to update line (${response.statusCode})',
      );
    }
    return QuotationLine.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<void> deleteLine(String quotationId, String lineId) async {
    final response = await _client.delete(
      '/api/v1/sal/quotations/$quotationId/lines/$lineId',
    );
    if (response.statusCode != 204) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to delete line (${response.statusCode})',
      );
    }
  }

  Future<SalesOrderConvertResult> convertToSalesOrder(String id) async {
    final response = await _client.post('/api/v1/sal/quotations/$id/convert-to-order');
    if (response.statusCode != 201) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to convert to sales order (${response.statusCode})',
      );
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return SalesOrderConvertResult(
      salesOrderId: body['sales_order_id'] as String,
      soNumber: body['so_number'] as String,
      message: body['message'] as String? ?? 'Sales order created',
    );
  }
}

class SalesOrderConvertResult {
  SalesOrderConvertResult({
    required this.salesOrderId,
    required this.soNumber,
    required this.message,
  });

  final String salesOrderId;
  final String soNumber;
  final String message;
}

class QuotationStatusEntry {
  QuotationStatusEntry({
    required this.fromStatus,
    required this.toStatus,
    this.reason,
    required this.changedOn,
  });

  final String fromStatus;
  final String toStatus;
  final String? reason;
  final String changedOn;

  factory QuotationStatusEntry.fromJson(Map<String, dynamic> json) =>
      QuotationStatusEntry(
        fromStatus: json['from_status'] as String,
        toStatus: json['to_status'] as String,
        reason: json['reason'] as String?,
        changedOn: '${json['changed_on']}',
      );
}
