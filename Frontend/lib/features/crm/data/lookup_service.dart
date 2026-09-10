import 'dart:convert';

import '../../../core/network/api_client.dart';

const defaultPipelineStages = [
  'QUALIFICATION',
  'TECHNICAL_EVAL',
  'BUDGET_VALIDATION',
  'PROPOSAL',
  'QUOTATION_ISSUED',
  'NEGOTIATION',
];

String? nextPipelineStage(List<String> stages, String current) {
  final idx = stages.indexOf(current);
  if (idx < 0 || idx >= stages.length - 1) return null;
  return stages[idx + 1];
}

const outcomeRequiredTypes = {'CALL', 'MEETING', 'TASK'};

class ActivityType {
  ActivityType({
    required this.activityTypeId,
    required this.code,
    required this.name,
    required this.isActive,
  });

  final String activityTypeId;
  final String code;
  final String name;
  final bool isActive;

  factory ActivityType.fromJson(Map<String, dynamic> json) => ActivityType(
        activityTypeId: json['activity_type_id'] as String,
        code: json['code'] as String,
        name: json['name'] as String,
        isActive: json['is_active'] as bool? ?? true,
      );
}

class ActivityOutcome {
  ActivityOutcome({
    required this.activityOutcomeId,
    required this.activityTypeCode,
    required this.code,
    required this.name,
    required this.isPositive,
    required this.isActive,
  });

  final String activityOutcomeId;
  final String activityTypeCode;
  final String code;
  final String name;
  final bool isPositive;
  final bool isActive;

  factory ActivityOutcome.fromJson(Map<String, dynamic> json) => ActivityOutcome(
        activityOutcomeId: json['activity_outcome_id'] as String,
        activityTypeCode: json['activity_type_code'] as String,
        code: json['code'] as String,
        name: json['name'] as String,
        isPositive: json['is_positive'] as bool? ?? false,
        isActive: json['is_active'] as bool? ?? true,
      );
}

class OpportunityStage {
  OpportunityStage({
    required this.opportunityStageId,
    required this.code,
    required this.name,
    required this.sequenceNo,
    required this.defaultProbability,
    required this.isClosed,
    required this.isActive,
  });

  final String opportunityStageId;
  final String code;
  final String name;
  final int sequenceNo;
  final int defaultProbability;
  final bool isClosed;
  final bool isActive;

  factory OpportunityStage.fromJson(Map<String, dynamic> json) => OpportunityStage(
        opportunityStageId: json['opportunity_stage_id'] as String,
        code: json['code'] as String,
        name: json['name'] as String,
        sequenceNo: json['sequence_no'] as int? ?? 0,
        defaultProbability: json['default_probability'] as int? ?? 0,
        isClosed: json['is_closed'] as bool? ?? false,
        isActive: json['is_active'] as bool? ?? true,
      );
}

class CrmLookups {
  const CrmLookups({
    required this.pipelineStages,
    required this.opportunityStatuses,
    required this.leadStatuses,
    required this.activityTypes,
    required this.activityStatuses,
  });

  final List<String> pipelineStages;
  final List<String> opportunityStatuses;
  final List<String> leadStatuses;
  final List<String> activityTypes;
  final List<String> activityStatuses;

  static const defaults = CrmLookups(
    pipelineStages: [],
    opportunityStatuses: [],
    leadStatuses: [],
    activityTypes: ['NOTE', 'CALL', 'MEETING', 'EMAIL', 'TASK'],
    activityStatuses: [],
  );

  factory CrmLookups.fromJson(Map<String, dynamic> json) => CrmLookups(
        pipelineStages: (json['pipeline_stages'] as List<dynamic>? ?? [])
            .map((e) => e as String)
            .toList(),
        opportunityStatuses: (json['opportunity_statuses'] as List<dynamic>? ?? [])
            .map((e) => e as String)
            .toList(),
        leadStatuses: (json['lead_statuses'] as List<dynamic>? ?? [])
            .map((e) => e as String)
            .toList(),
        activityTypes: (json['activity_types'] as List<dynamic>? ?? [])
            .map((e) => e as String)
            .toList(),
        activityStatuses: (json['activity_statuses'] as List<dynamic>? ?? [])
            .map((e) => e as String)
            .toList(),
      );
}

class LookupService {
  LookupService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  CrmLookups? _cache;

  void clearCache() => _cache = null;

  Future<CrmLookups> fetch() async {
    if (_cache != null) return _cache!;
    final res = await _client.get('/api/v1/crm/lookups');
    if (res.statusCode != 200) {
      return CrmLookups.defaults;
    }
    _cache = CrmLookups.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    return _cache!;
  }

  Future<List<String>> pipelineStageCodes() async {
    final lookups = await fetch();
    return lookups.pipelineStages.isNotEmpty
        ? lookups.pipelineStages
        : defaultPipelineStages;
  }

  Future<List<String>> activityTypes() async {
    final lookups = await fetch();
    return lookups.activityTypes.isNotEmpty
        ? lookups.activityTypes
        : CrmLookups.defaults.activityTypes;
  }

  Future<List<ActivityType>> listActivityTypes({
    bool includeInactive = false,
  }) async {
    final res = await _client.get(
      '/api/v1/crm/activity-types',
      query: {'include_inactive': '$includeInactive'},
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to load activity types');
    }
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (data['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(ActivityType.fromJson)
        .toList();
  }

  Future<ActivityType> createActivityType({
    required String code,
    required String name,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/activity-types',
      body: {'code': code, 'name': name},
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to create activity type');
    }
    clearCache();
    return ActivityType.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<ActivityType> updateActivityType(
    String activityTypeId, {
    bool? isActive,
    String? name,
  }) async {
    final body = <String, dynamic>{};
    if (isActive != null) body['is_active'] = isActive;
    if (name != null) body['name'] = name;
    final res = await _client.patch(
      '/api/v1/crm/activity-types/$activityTypeId',
      body: body,
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to update activity type');
    }
    clearCache();
    return ActivityType.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<List<ActivityOutcome>> listActivityOutcomes({
    String? activityTypeCode,
    bool includeInactive = false,
  }) async {
    final query = <String, String>{
      'include_inactive': '$includeInactive',
      if (activityTypeCode != null) 'activity_type_code': activityTypeCode,
    };
    final res = await _client.get('/api/v1/crm/activity-outcomes', query: query);
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to load outcomes');
    }
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (data['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(ActivityOutcome.fromJson)
        .toList();
  }

  Future<ActivityOutcome> createActivityOutcome({
    required String activityTypeCode,
    required String code,
    required String name,
    bool isPositive = false,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/activity-outcomes',
      body: {
        'activity_type_code': activityTypeCode,
        'code': code,
        'name': name,
        'is_positive': isPositive,
      },
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to create outcome');
    }
    clearCache();
    return ActivityOutcome.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<ActivityOutcome> updateActivityOutcome(
    String outcomeId, {
    bool? isActive,
    String? name,
    bool? isPositive,
  }) async {
    final body = <String, dynamic>{};
    if (isActive != null) body['is_active'] = isActive;
    if (name != null) body['name'] = name;
    if (isPositive != null) body['is_positive'] = isPositive;
    final res = await _client.patch(
      '/api/v1/crm/activity-outcomes/$outcomeId',
      body: body,
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to update outcome');
    }
    clearCache();
    return ActivityOutcome.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<List<OpportunityStage>> listOpportunityStages({
    bool includeInactive = true,
  }) async {
    final res = await _client.get(
      '/api/v1/crm/opportunity-stages',
      query: {'include_inactive': '$includeInactive'},
    );
    if (res.statusCode != 200) {
      return const [];
    }
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (data['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(OpportunityStage.fromJson)
        .toList();
  }

  Future<OpportunityStage> createOpportunityStage({
    required String code,
    required String name,
    int defaultProbability = 0,
    bool isClosed = false,
  }) async {
    final res = await _client.post(
      '/api/v1/crm/opportunity-stages',
      body: {
        'code': code,
        'name': name,
        'default_probability': defaultProbability,
        'is_closed': isClosed,
      },
    );
    if (res.statusCode != 201) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to create stage');
    }
    clearCache();
    return OpportunityStage.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<OpportunityStage> updateOpportunityStage(
    String stageId, {
    bool? isActive,
    String? name,
  }) async {
    final body = <String, dynamic>{};
    if (isActive != null) body['is_active'] = isActive;
    if (name != null) body['name'] = name;
    final res = await _client.patch(
      '/api/v1/crm/opportunity-stages/$stageId',
      body: body,
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to update stage');
    }
    clearCache();
    return OpportunityStage.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<List<OpportunityStage>> reorderOpportunityStages(
    List<String> stageIds,
  ) async {
    final res = await _client.put(
      '/api/v1/crm/opportunity-stages/reorder',
      body: {'stage_ids': stageIds},
    );
    if (res.statusCode != 200) {
      throw Exception(_client.extractError(res.body) ?? 'Failed to reorder stages');
    }
    clearCache();
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (data['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(OpportunityStage.fromJson)
        .toList();
  }
}
