import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQml 2.15

Item {
    property bool isStreaming: true
    property bool isCameraOpen: true
    property bool isSelectingPort: false
    property bool isPlotting: false
    property string buttonCameraText: qsTr("Take a Photo")
    property string buttonRetakeText: qsTr("Retake")
    property string buttonProcessText: qsTr("Process the Photo")
    property string buttonPlotText: qsTr("Start Plotting the Image")

    // all connections coming from presenter
    Connections{
        target: presenter
        function onNewFrame() {
            image.reload()
        }
        function onStartedStreaming() {
            isStreaming = true
            isCameraOpen = true
            isSelectingPort = false
            isPlotting = false
            portModel.clear()
            console.log("Started Streaming")
        }
        function onFinishedStreaming() { // camera is still on just dont provide new images
            isStreaming = false
            isCameraOpen = true
            isSelectingPort = false
            isPlotting = false
            console.log("Finished Streaming")
        }
        function onCameraClosed() { // camera and its thread destroyed
            isStreaming = false
            isCameraOpen = false
            isSelectingPort = true
            isPlotting = false
            console.log("Camera Closed")
        }
        function onPlottingStarted() {
            isStreaming = false
            isCameraOpen = false
            isSelectingPort = false
            isPlotting = true
            buttonRetake.enabled = false
            console.log("Started Plotting")
        }
        function onPlottingStopped() {
            buttonRetake.enabled = true
            console.log("Finished Plotting")
        }
        function onProgressUpdate(progress) {
            circularProgress.currentValue = progress
            circularProgress.text = progress.toFixed(2) + "%"
            if(progress === 100) delay(1000, circularProgress.text = "DONE!")
        }
        function onSerialPorts(ports) {
            portModel.append({text: ports})
            comboBoxSerial.model = portModel
        }
        function onConnectionTimeout(error) {
            console.log(error)
            buttonRetake.clicked()
        }
    }

    function delay(delayTime, cb) {
        timer.interval = delayTime
        timer.repeat = false
        timer.triggered.connect(cb)
        timer.start()
    }
    Timer {
        id: timer
    }

    ListModel {
        id: portModel
    }

    Rectangle {
        id: rectangle
        anchors.fill: parent
        color: "#054854"
        border.color: "#53565A"
        border.width: 5
        clip: true

        // Background image for Application, taken from Turkish-German University
        Image {
            id: background
            source: "../tdu_background.png"
            anchors.fill: parent
            anchors.margins: parent.border.width
            z: 0
        }

        Image {
            id: tdu_logo
            source: "../tdu_logo.png" // Turkish-German University Logo
            antialiasing: true
            sourceSize.width: 100
            sourceSize.height: 100
            mipmap: true
            width: parent.width / 10
            height: width
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 15
            z: 0
        }

        Image {
            id: tub_logo
            source: "../tub_logo.png" // Technical University Of Berlin Logo
            antialiasing: true
            sourceSize.width: 100
            sourceSize.height: 100
            mipmap: true
            width: parent.width / 10
            height: width
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 15
            z: 0
        }

        // this is where image will be displayed
        Rectangle {
            id: imageRectangle
            width: Math.round(0.6*rectangle.width)
            height: Math.round((1/1.414)*width) // "A" paper ratio
            visible: !isPlotting
            anchors.top: parent.top
            anchors.topMargin: 50
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 50
            color: "#0096b4"
            radius: 10
            z: 1

            Image {
                id: image
                source: "image://camera_provider/frame"
                anchors.margins: 10
                sourceSize.width: parent.width
                sourceSize.height: parent.height // "A" paper ratio
                cache: false
                smooth: true
                anchors.fill: parent
                property bool counter: false
                function reload(){
                    counter = !counter
                    source = "image://camera_provider/frame?id=" + counter
                }
            }

            MouseArea {
                anchors.fill: parent
                onClicked: presenter.openPreviewImage(rectangle.width, rectangle.height)
            }
        }

        // to show plotting process, calculated from total number of gcode line
        CircularProgress {
            id: circularProgress
            anchors.top: parent.top
            visible: isPlotting
            anchors.topMargin: 50
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 50
            width: 0.45*parent.width
            height: width
            z: 1
        }

        Row {
            id: row
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 50
            anchors.top: imageRectangle.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 50
            height: children.height
            z: 1

            CustomButton {
                id: buttonCamera
                visible: isStreaming
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonCameraText
                onClicked: presenter.stopCamera()
            }

            CustomButton {
                id: buttonRetake
                visible: !isStreaming
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonRetakeText
                onClicked: presenter.startCamera()
            }

            CustomButton {
                id: buttonProcess
                visible: !isStreaming && isCameraOpen
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonProcessText
                onClicked: presenter.processImage()
            }

            CustomComboBox {
                id:comboBoxSerial
                visible: isSelectingPort
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                onCurrentTextChanged: {
                    currentText == "" ? buttonPlot.enabled = false: buttonPlot.enabled = true
                }
            }

            CustomButton {
                id: buttonPlot
                visible: isSelectingPort
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonPlotText
                onClicked: presenter.startPlotting(comboBoxSerial.currentText)
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
