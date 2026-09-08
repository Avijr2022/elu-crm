import 'package:flutter/material.dart';

/// Shared CRM spacing and shape tokens (CustomerTracker rhythm, CRM brand).
abstract final class CrmSpacing {
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 24;
  static const double page = md;
}

abstract final class CrmRadii {
  static const double search = 28;
  static const double card = 12;
  static const double section = 16;
}

InputDecoration crmSearchDecoration({
  required String hintText,
  Widget? suffixIcon,
}) {
  return InputDecoration(
    hintText: hintText,
    prefixIcon: const Icon(Icons.search),
    suffixIcon: suffixIcon,
    filled: true,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(CrmRadii.search),
      borderSide: BorderSide.none,
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(CrmRadii.search),
      borderSide: BorderSide.none,
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(CrmRadii.search),
      borderSide: const BorderSide(width: 1.5),
    ),
    contentPadding: const EdgeInsets.symmetric(horizontal: CrmSpacing.md),
  );
}
