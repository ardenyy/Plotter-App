import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

ApplicationWindow{
    id: root
    minimumWidth: 1000
    minimumHeight: 650
    maximumWidth: height * 1.7
    visible: true
    color: "#0096B4"
    title: qsTr("Plotter App - Turkish-German University")

    Loader {
        id: pageLoader
        anchors.fill: parent
        anchors.margins: 20
        source: Qt.resolvedUrl("Home.qml")
        clip: true
    }
}
