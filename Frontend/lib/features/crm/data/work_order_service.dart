import 'dart:convert';

import '../../../core/network/api_client.dart';

class WorkOrder {
  WorkOrder({
    required this.workOrderId,
    required this.woNumber,
    required this.status,
    required this.createdOn,
    this.opportunityId,
    this.customerId,
    this.salesOrderId,
    this.soNumber,
  });

  final String workOrderId;
  final String woNumber;
  final String? opportunityId;
  final String? customerId;
  final String? salesOrderId;
  final String? soNumber;
  final String status;
  final String createdOn;

  factory WorkOrder.fromJson(Map<String, dynamic> json) => WorkOrder(
        workOrderId: json['work_order_id'] as String,
        woNumber: json['wo_number'] as String,
        opportunityId: json['opportunity_id'] as String?,
        customerId: json['customer_id'] as String?,
        salesOrderId: json['sales_order_id'] as String?,
        soNumber: json['so_number'] as String?,
        status: json['status'] as String,
        createdOn: '${json['created_on']}',
      );
}

class WorkOrderListResult {
  WorkOrderListResult({required this.items, required this.total});

  final List<WorkOrder> items;
  final int total;

  factory WorkOrderListResult.fromJson(Map<String, dynamic> json) =>
      WorkOrderListResult(
        items: (json['items'] as List<dynamic>)
            .map((e) => WorkOrder.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int,
      );
}

class WorkOrderService {
  WorkOrderService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<WorkOrderListResult> list({int page = 1, String? status}) async {
    final query = <String, String>{
      'page': '$page',
      'page_size': '25',
      if (status != null && status.isNotEmpty) 'status': status,
    };
    final response = await _client.get('/api/v1/prj/work-orders', query: query);
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load work orders (${response.statusCode})',
      );
    }
    return WorkOrderListResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<WorkOrder> getById(String id) async {
    final response = await _client.get('/api/v1/prj/work-orders/$id');
    if (response.statusCode != 200) {
      throw Exception(
        _client.extractError(response.body) ??
            'Failed to load work order (${response.statusCode})',
      );
    }
    return WorkOrder.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
