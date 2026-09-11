class CrmRbac {
  static const salesRoles = {
    'SALES_EXECUTIVE',
    'SALES_MANAGER',
    'TENANT_ADMIN',
    'PLATFORM_ADMIN',
  };
  static const managerRoles = {
    'SALES_MANAGER',
    'TENANT_ADMIN',
    'PLATFORM_ADMIN',
  };

  /// BFS-PF-004 §12 / ELU-UI-PF §1: organization management is Tenant Admin only.
  /// Deliberately a role set (not a permission check) because [hasPermission]
  /// grants PLATFORM_ADMIN a universal bypass, which would contradict the
  /// read-only Platform Admin rule for this module.
  static const organizationRoles = {'TENANT_ADMIN'};

  static bool hasPermission(Map<String, dynamic>? profile, String code) {
    if (profile == null) return false;
    if (profile['role_code'] == 'PLATFORM_ADMIN') return true;
    final perms = profile['permissions'];
    if (perms is List) {
      return perms.contains(code);
    }
    return false;
  }

  static bool isSales(String? role) =>
      role != null && salesRoles.contains(role);
  static bool isManager(String? role) =>
      role != null && managerRoles.contains(role);

  static bool canCloseWon(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'opportunity.approve') ||
      isManager(profile?['role_code'] as String?);

  static bool canViewPipeline(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'opportunity.read') && canCloseWon(profile);

  static bool canCreateLead(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'lead.create') ||
      isSales(profile?['role_code'] as String?);

  static bool canCreateActivity(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'activity.create') ||
      isSales(profile?['role_code'] as String?);

  static bool canManageOrganizations(Map<String, dynamic>? profile) =>
      organizationRoles.contains(profile?['role_code'] as String?);

  static bool canUpdateCustomer(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'customer.update') ||
      isManager(profile?['role_code'] as String?);

  static bool canCreateCustomer(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'customer.create') ||
      isSales(profile?['role_code'] as String?);

  static bool canConvertLead(
    Map<String, dynamic>? profile, {
    required bool hasOpportunityEdition,
    required bool hasCustomerEdition,
  }) =>
      (hasOpportunityEdition || hasCustomerEdition) &&
      (hasPermission(profile, 'lead.convert') ||
          isManager(profile?['role_code'] as String?));

  static bool canQualifyLead(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'lead.qualify') ||
      isSales(profile?['role_code'] as String?);

  static bool canDisqualifyLead(Map<String, dynamic>? profile) =>
      hasPermission(profile, 'lead.disqualify') ||
      isManager(profile?['role_code'] as String?);
}
