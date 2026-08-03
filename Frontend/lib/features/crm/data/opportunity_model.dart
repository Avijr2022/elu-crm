class Opportunity {
  Opportunity({
    required this.opportunityId,
    required this.opportunityNumber,
    required this.name,
    this.companyName,
    required this.stage,
    required this.status,
    required this.opportunityValue,
    required this.currencyCode,
    required this.probability,
    this.expectedCloseDate,
    this.sourceLeadId,
    this.notes,
    required this.weightedValue,
    this.createdOn,
  });

  final String opportunityId;
  final String opportunityNumber;
  final String name;
  final String? companyName;
  final String stage;
  final String status;
  final double opportunityValue;
  final String currencyCode;
  final int probability;
  final DateTime? expectedCloseDate;
  final String? sourceLeadId;
  final String? notes;
  final double weightedValue;
  final DateTime? createdOn;

  factory Opportunity.fromJson(Map<String, dynamic> json) {
    return Opportunity(
      opportunityId: json['opportunity_id'] as String,
      opportunityNumber: json['opportunity_number'] as String,
      name: json['name'] as String,
      companyName: json['company_name'] as String?,
      stage: json['stage'] as String,
      status: json['status'] as String,
      opportunityValue:
          double.tryParse(json['opportunity_value']?.toString() ?? '') ?? 0,
      currencyCode: (json['currency_code'] as String?) ?? 'INR',
      probability: int.tryParse(json['probability']?.toString() ?? '') ?? 0,
      expectedCloseDate: json['expected_close_date'] != null
          ? DateTime.tryParse(json['expected_close_date'].toString())
          : null,
      sourceLeadId: json['source_lead_id'] as String?,
      notes: json['notes'] as String?,
      weightedValue:
          double.tryParse(json['weighted_value']?.toString() ?? '') ?? 0,
      createdOn: json['created_on'] != null
          ? DateTime.tryParse(json['created_on'] as String)
          : null,
    );
  }
}

class OpportunityListResult {
  OpportunityListResult({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  final List<Opportunity> items;
  final int total;
  final int page;
  final int pageSize;

  factory OpportunityListResult.fromJson(Map<String, dynamic> json) {
    final raw = (json['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return OpportunityListResult(
      items: raw.map(Opportunity.fromJson).toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 25,
    );
  }
}

class PipelineStageBucket {
  PipelineStageBucket({
    required this.stage,
    required this.count,
    required this.totalValue,
    required this.weightedValue,
    required this.items,
  });

  final String stage;
  final int count;
  final double totalValue;
  final double weightedValue;
  final List<Opportunity> items;

  factory PipelineStageBucket.fromJson(Map<String, dynamic> json) {
    final raw = (json['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return PipelineStageBucket(
      stage: json['stage'] as String,
      count: json['count'] as int? ?? 0,
      totalValue: double.tryParse(json['total_value']?.toString() ?? '') ?? 0,
      weightedValue:
          double.tryParse(json['weighted_value']?.toString() ?? '') ?? 0,
      items: raw.map(Opportunity.fromJson).toList(),
    );
  }
}

class PipelineResult {
  PipelineResult({required this.stages});

  final List<PipelineStageBucket> stages;

  factory PipelineResult.fromJson(Map<String, dynamic> json) {
    final raw = (json['stages'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return PipelineResult(
      stages: raw.map(PipelineStageBucket.fromJson).toList(),
    );
  }
}
