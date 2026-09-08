import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import 'opportunities_controller.dart';

Future<bool?> showOpportunityFormDialog(
  BuildContext context,
  OpportunitiesController controller,
) {
  return context.push<bool>(CrmRoutes.opportunitiesNew).then((v) {
    if (v == true) controller.load();
    return v;
  });
}
