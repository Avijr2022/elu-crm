// ignore_for_file: unnecessary_import, unused_import

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class DropdownDemo extends StatefulWidget {
  const DropdownDemo({super.key});
  @override
  State<DropdownDemo> createState() => _DropdownDemoState();
}

class _DropdownDemoState extends State<DropdownDemo> {
  String dropdownValue = 'Tarak Basak';
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // appBar: AppBar(
      //   title: const Text(
      //     'Assigned User List',
      //     style: TextStyle(fontSize: 17),
      //   ),
      //   elevation: 0,
      //   backgroundColor: const Color.fromARGB(255, 91, 92, 92),
      //   leading: IconButton(
      //       onPressed: () {
      //         Navigator.pop(context);
      //       },
      //       icon: const Icon(
      //         Icons.arrow_back_ios,
      //         size: 20,
      //         color: Color.fromARGB(255, 245, 245, 245),
      //       )),
      //   systemOverlayStyle: SystemUiOverlayStyle.dark,
      // ),
      body: Center(
        child: Column(
          children: [
            const SizedBox(
              height: 25,
            ),
            DropdownButton<String>(
              value: dropdownValue,
              items: <String>[
                'Tarak Basak',
                'Kedar Gupra',
                'Akram Mallik',
                'Samik Dey'
              ].map<DropdownMenuItem<String>>((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(
                    value,
                    style: const TextStyle(fontSize: 30),
                  ),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  dropdownValue = newValue!;
                });
              },
            ),
            //   const SizedBox(
            //     height: 20,
            //   ),
            //   // Text(
            //   //   // 'Selected Value: $dropdownValue',
            //   //   style: const TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
            //   // )
          ],
        ),
      ),
    );
  }
}
