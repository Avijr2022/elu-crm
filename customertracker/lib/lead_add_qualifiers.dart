// ignore_for_file: sort_child_properties_last, unused_field, no_leading_underscores_for_local_identifiers, unused_local_variable, unused_element, non_constant_identifier_names, use_key_in_widget_constructors, no_logic_in_create_state, unnecessary_const, avoid_print, prefer_typing_uninitialized_variables, unused_import

// import 'package:customertracker/buttontoggleswitch.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/widgets/my_text_field.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class QualifiersLayout extends StatefulWidget {
  const QualifiersLayout({super.key});
  @override
  State<QualifiersLayout> createState() => QualifiersLayoutState();
}

class QualifiersLayoutState extends State<QualifiersLayout> {
  bool isToggled = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        drawer: const NavDrawer(),
        body: Container(
          padding: const EdgeInsets.only(left: 10.0, right: 10.0),
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover2.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: Column(children: [
            const Row(children: <Widget>[
              Padding(padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0)),
              Icon(Icons.list),
              SizedBox(width: 7),
              Text(
                'Product Group    ',
                maxLines: 1,
                textAlign: TextAlign.left,
              ),
              SizedBox(
                width: 139,
              ),
              Icon(Icons.add_circle_outline),
            ]),
            const Divider(),
            const Row(children: <Widget>[
              Padding(padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0)),
              Icon(FontAwesomeIcons.networkWired),
              SizedBox(width: 10),
              Text(
                'Customer Group',
                maxLines: 1,
                textAlign: TextAlign.left,
              ),
              SizedBox(
                width: 140,
              ),
              Icon(Icons.add_circle_outline),
            ]),
            const Divider(),
            const MyTextField(
              icon: Icon(Icons.currency_rupee),
              label: 'Deal Size',
              minLines: 1,
              // maxLines: 3,
            ),
            const SizedBox(height: 5),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(FontAwesomeIcons.starHalfStroke),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'Lead Potential',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 10),
            // const Divider(),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label:
                            //TextButton(onPressed: onPressed, child: child),
                            Text("Low"),
                        backgroundColor: Color.fromARGB(75, 0, 0, 0),
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      Chip(
                        padding: EdgeInsets.only(
                            left: 0.0, top: 0.0, right: 0.0, bottom: 0.0),
                        label: Text("Medium"),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(
              height: 5,
            ),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label: Text("High"),
                      ),
                      Chip(
                        label: Text("Not Relevant"),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 5),
            const Divider(),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(FontAwesomeIcons.squareCaretDown),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'Lead Stage',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 10),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label:
                            //TextButton(onPressed: onPressed, child: child),
                            Text("Open"),
                        backgroundColor: Color.fromARGB(75, 0, 0, 0),
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      Chip(
                        padding: EdgeInsets.only(
                            left: 0.0, top: 0.0, right: 0.0, bottom: 0.0),
                        label: Text("Contacted"),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(
              height: 5,
            ),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label: Text("Qualified"),
                      ),
                      Chip(
                        label: Text("Customer"),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const Divider(),
            const Row(children: <Widget>[
              Padding(padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0)),
              Icon(FontAwesomeIcons.tags),
              SizedBox(width: 15),
              Text(
                'Tags               ',
                maxLines: 1,
                textAlign: TextAlign.left,
              ),
              SizedBox(width: 150),
              Icon(Icons.add_circle_outline),
            ]),
          ]),
        ));
  }

// @override
// State<StatefulWidget> createState() {
//   throw UnimplementedError();
}
