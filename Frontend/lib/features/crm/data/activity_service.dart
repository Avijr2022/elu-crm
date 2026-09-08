import 'dart:convert';



import '../../../core/network/api_client.dart';



class ActivityItem {

  ActivityItem({

    required this.activityId,

    required this.activityTypeCode,

    required this.subject,

    this.description,

    required this.status,

    required this.entityType,

    required this.entityId,

    required this.createdOn,

    this.dueOn,

    this.outcomeCode,

  });



  final String activityId;

  final String activityTypeCode;

  final String subject;

  final String? description;

  final String status;

  final String entityType;

  final String entityId;

  final DateTime createdOn;

  final DateTime? dueOn;

  final String? outcomeCode;

  factory ActivityItem.fromJson(Map<String, dynamic> json) => ActivityItem(
        activityId: json['activity_id'] as String,
        activityTypeCode: json['activity_type_code'] as String,
        subject: json['subject'] as String,
        description: json['description'] as String?,
        status: json['status'] as String,
        entityType: json['entity_type'] as String,
        entityId: json['entity_id'] as String,
        createdOn: DateTime.parse(json['created_on'] as String),
        dueOn: json['due_on'] != null
            ? DateTime.tryParse(json['due_on'] as String)
            : null,
        outcomeCode: json['outcome_code'] as String?,
      );
}



class ActivityCreatePayload {

  ActivityCreatePayload({

    required this.entityType,

    required this.entityId,

    required this.subject,

    this.description,

    this.activityTypeCode = 'NOTE',
    this.outcomeCode,
    this.dueOn,
    this.status,
  });

  final String entityType;
  final String entityId;
  final String subject;
  final String? description;
  final String activityTypeCode;
  final String? outcomeCode;
  final DateTime? dueOn;
  final String? status;

  Map<String, dynamic> toJson() => {
        'entity_type': entityType,
        'entity_id': entityId,
        'subject': subject,
        if (description != null) 'description': description,
        'activity_type_code': activityTypeCode,
        if (outcomeCode != null) 'outcome_code': outcomeCode,
        if (dueOn != null) 'due_on': dueOn!.toUtc().toIso8601String(),
        if (status != null) 'status': status,
      };
}



class ActivityService {

  ActivityService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;



  Future<List<ActivityItem>> timeline({

    required String entityType,

    required String entityId,

  }) async {

    final res = await _client.get(

      '/api/v1/crm/activities/timeline',

      query: {'entity_type': entityType, 'entity_id': entityId},

    );

    if (res.statusCode != 200) {

      throw Exception(_client.extractError(res.body) ?? 'Failed to load activities');

    }

    final data = jsonDecode(res.body) as Map<String, dynamic>;

    return (data['items'] as List<dynamic>? ?? [])

        .cast<Map<String, dynamic>>()

        .map(ActivityItem.fromJson)

        .toList();

  }

  Future<List<ActivityItem>> list({String view = 'my'}) async {
    final res = await _client.get(
      '/api/v1/crm/activities',
      query: {'view': view},
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to load activities');
    }
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (data['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(ActivityItem.fromJson)
        .toList();
  }

  Future<ActivityItem> create(ActivityCreatePayload payload) async {

    final res = await _client.post(

      '/api/v1/crm/activities',

      body: jsonEncode(payload.toJson()),

    );

    if (res.statusCode != 201) {

      throw Exception(_client.extractError(res.body) ?? 'Failed to create activity');

    }

    return ActivityItem.fromJson(jsonDecode(res.body) as Map<String, dynamic>);

  }

}


