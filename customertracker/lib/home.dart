import 'package:customertracker/side_menu_app.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class BaseLayout extends StatelessWidget {
  const BaseLayout({super.key});

  String? get asset => null;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        drawer: const NavDrawer(),
        appBar: AppBar(
          title: const Text(
            'Euphoria Infotech (I) Pvt Ltd',
            style: TextStyle(fontSize: 17),
          ),
          titleTextStyle: const TextStyle(
              color: Color.fromARGB(255, 250, 252, 252),
              fontWeight: FontWeight.w500,
              fontSize: 25),
          elevation: 0,
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          systemOverlayStyle: SystemUiOverlayStyle.dark,
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: TextField(
            maxLines: 1,
            style: const TextStyle(fontSize: 17),
            textAlignVertical: TextAlignVertical.center,
            decoration: InputDecoration(
              filled: true,
              prefixIcon:
                  Icon(Icons.search, color: Theme.of(context).iconTheme.color),
              border: const OutlineInputBorder(
                  borderSide: BorderSide.none,
                  borderRadius: BorderRadius.all(Radius.circular(30))),
              fillColor: Theme.of(context).inputDecorationTheme.fillColor,
              contentPadding: EdgeInsets.zero,
              hintText: 'Search',
            ),
          ),
        ));
  }
}
