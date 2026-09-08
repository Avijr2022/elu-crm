class Lead {
  Lead({
    required this.leadId,
    required this.leadNumber,
    required this.fullName,
    this.companyName,
    this.email,
    this.phone,
    required this.status,
    required this.estimatedValue,
    required this.currencyCode,
    this.notes,
    this.ownerId,
    this.createdOn,
    this.modifiedOn,
  });

  final String leadId;
  final String leadNumber;
  final String fullName;
  final String? companyName;
  final String? email;
  final String? phone;
  final String status;
  final double estimatedValue;
  final String currencyCode;
  final String? notes;
  final String? ownerId;
  final DateTime? createdOn;
  final DateTime? modifiedOn;

  bool get isTerminal => status == 'CONVERTED' || status == 'DISQUALIFIED';

  bool get canQualify =>
      !isTerminal &&
      {'NEW', 'UNDER_QUALIFICATION', 'NURTURE', 'ON_HOLD'}.contains(status);

  bool get canDisqualify => !isTerminal;

  factory Lead.fromJson(Map<String, dynamic> json) {
    return Lead(
      leadId: json['lead_id'] as String,
      leadNumber: json['lead_number'] as String,
      fullName: json['full_name'] as String,
      companyName: json['company_name'] as String?,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      status: json['status'] as String,
      estimatedValue:
          double.tryParse(json['estimated_value']?.toString() ?? '') ?? 0,
      currencyCode: (json['currency_code'] as String?) ?? 'INR',
      notes: json['notes'] as String?,
      ownerId: json['owner_id'] as String?,
      createdOn: json['created_on'] != null
          ? DateTime.tryParse(json['created_on'] as String)
          : null,
      modifiedOn: json['modified_on'] != null
          ? DateTime.tryParse(json['modified_on'] as String)
          : null,
    );
  }
}

class LeadListResult {
  LeadListResult({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  final List<Lead> items;
  final int total;
  final int page;
  final int pageSize;

  factory LeadListResult.fromJson(Map<String, dynamic> json) {
    final raw = (json['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return LeadListResult(
      items: raw.map(Lead.fromJson).toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 25,
    );
  }
}
