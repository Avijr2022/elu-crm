// ignore_for_file: sort_child_properties_last, unused_field, no_leading_underscores_for_local_identifiers, unused_local_variable, unused_element, non_constant_identifier_names, use_key_in_widget_constructors, no_logic_in_create_state, unnecessary_const, avoid_print, prefer_typing_uninitialized_variables, unused_import, camel_case_types

// import 'package:customertracker/buttontoggleswitch.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/widgets/my_text_field.dart';
import 'package:flutter/material.dart';

import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class QuoteSettingLayout extends StatefulWidget {
  const QuoteSettingLayout({super.key});
  @override
  State<QuoteSettingLayout> createState() => QuoteSettingLayoutState();
}

class QuoteSettingLayoutState extends State<QuoteSettingLayout> {
  bool isToggled = false;

  quotesettingLayoutState() {
    bool isSwitchOn = false;
  }

  @override
  Widget build(BuildContext context) {
    var GFToggleType;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        leading: IconButton(
            onPressed: () {
              Navigator.pop(context);
            },
            icon: const Icon(
              Icons.arrow_back_ios,
              size: 15,
              color: Color.fromARGB(255, 248, 247, 247),
            )),
        actions: <Widget>[
          const Padding(padding: EdgeInsets.only(right: 60.0)),
          IconButton(
            onPressed: () {
              Navigator.pop(context);
            },
            icon: const Icon(
              Icons.save,
              size: 30,
              color: Color.fromARGB(255, 248, 247, 247),
            ),
          ),
        ],
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 10.0, right: 10.0),
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover2.jpg'),
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }
}
