import 'dart:convert';
import 'dart:io';

import 'package:agrotech_hackat/view/dialogs/selectImage.dart';
import 'package:agrotech_hackat/widgets/button.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import '../constants/colors.dart';
import '../size_config.dart';

class Scan extends StatefulWidget {
  const Scan({Key? key}) : super(key: key);

  @override
  State<Scan> createState() => _ScanState();
}

class _ScanState extends State<Scan> {
  bool isLoading = false;
  String clas = "";
  String confidence = "";
  List treatments = [];
  bool checked = false;
  checkImage(File image) async {
    setState(() {
      isLoading = true;
    });

    var url =
        "https://us-central1-disease-prediction-352706.cloudfunctions.net/predict";

    var request = http.MultipartRequest('POST', Uri.parse(url));
    request.files.add(await http.MultipartFile.fromPath('file', image.path));
    var resp = await request.send();
    //return resp.reasonPhrase;
    if (resp.statusCode == 200) {
      final respStr = await resp.stream.bytesToString();
      print(respStr);
      var json = jsonDecode(respStr);

      setState(() {
        isLoading = false;
        clas = json['class'];
        confidence = json['confidence'].toString();
        treatments = json['treatment'];
        checked = true;
      });
    }
  }

  XFile? logoFile;
  bool logoAvailable = false;
  File? imageFile;
  pickLogoFromGallery(ImageSource source) async {
    var image = await ImagePicker().pickImage(source: source);
    setState(() {
      logoFile = image;
      if (logoFile != null) {
        logoAvailable = true;
        Get.back();
        imageFile = File(image!.path);

        // String img64 = base64Encode(bytes);
        // print(img64);
        // storeLogo64 = img64;
        checkImage(imageFile!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: isLoading
          ? Center(
              child: CircularProgressIndicator(),
            )
          : !checked
              ? Center(
                  child: button("Scan", () {
                  selectImageDialog(context, pickLogoFromGallery);
                }, white, mainGreen, mainGreen, h(68, context),
                      w(200, context)))
              : Padding(
                  padding: EdgeInsets.only(
                      right: w(24, context),
                      left: w(24, context),
                      top: h(20, context)),
                  child: SafeArea(
                    child: Column(children: [
                      Expanded(
                          child: ListView(children: [
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: SizedBox(
                              height: h(300, context),
                              child: Image.file(
                                File(imageFile!.path),
                                fit: BoxFit.contain,
                              )),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(),
                          child: Text("Name of the disease",
                              style: TextStyle(
                                  fontSize: w(14, context),
                                  fontWeight: FontWeight.w400,
                                  color: grey)),
                        ),
                        SizedBox(
                          //height: h(200, context),
                          width: w(200, context),
                          child: Text(clas,
                              style: TextStyle(
                                  fontSize: w(14, context),
                                  fontWeight: FontWeight.w600,
                                  color: black)),
                        ),
                        Padding(
                          padding: EdgeInsets.only(top: h(20, context)),
                          child: Text("Confidence",
                              style: TextStyle(
                                  fontSize: w(14, context),
                                  fontWeight: FontWeight.w400,
                                  color: grey)),
                        ),
                        SizedBox(
                          //height: h(200, context),
                          width: w(200, context),
                          child: Text(confidence,
                              style: TextStyle(
                                  fontSize: w(14, context),
                                  fontWeight: FontWeight.w600,
                                  color: black)),
                        ),
                        Padding(
                          padding: EdgeInsets.only(top: h(24, context)),
                          child: Text("Treatment",
                              style: TextStyle(
                                  fontSize: w(14, context),
                                  fontWeight: FontWeight.w400,
                                  color: grey)),
                        ),
                        ListView.builder(
                            itemCount: treatments.length,
                            shrinkWrap: true,
                            physics: NeverScrollableScrollPhysics(),
                            itemBuilder: ((context, index) => Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Text(treatments[index],
                                      style: TextStyle(
                                          fontSize: w(14, context),
                                          fontWeight: FontWeight.w600,
                                          color: black)),
                                ))),
                      ]))
                    ]),
                  ),
                ),
    );
  }
}
