// 百度地图API功能
let map = new BMap.Map("map"); // 创建Map实例
map.centerAndZoom(new BMap.Point(123, 31.001), 13); // 初始化地图,设置中心点坐标和地图级别
map.enableScrollWheelZoom(true); //开启鼠标滚轮缩放

let ship0, ship1, ship2, ship3, ship4;

// init();

function init() {
	let shipIcon = new BMap.Icon("/static/res/ship/freighter_min.png", new BMap.Size(141, 25));
	ship0 = new BMap.Marker(new BMap.Point(0, 0), { icon: shipIcon });
	map.addOverlay(ship0);

	let shipIcon1 = new BMap.Icon("/static/res/ship/freighter1_min.png", new BMap.Size(141, 25));
	ship1 = new BMap.Marker(new BMap.Point(0, 0), { icon: shipIcon1 });
	map.addOverlay(ship1);

	let shipIcon2 = new BMap.Icon("/static/res/ship/freighter2_min.png", new BMap.Size(105, 25));
	ship2 = new BMap.Marker(new BMap.Point(0, 0), { icon: shipIcon2 });
	map.addOverlay(ship2);

	let shipIcon3 = new BMap.Icon("/static/res/ship/freighter3_min.png", new BMap.Size(113, 25));
	ship3 = new BMap.Marker(new BMap.Point(0, 0), { icon: shipIcon3 });
	map.addOverlay(ship3);

	let shipIcon4 = new BMap.Icon("/static/res/ship/freighter4_min.png", new BMap.Size(133, 25));
	ship4 = new BMap.Marker(new BMap.Point(0, 0), { icon: shipIcon4 });
	map.addOverlay(ship4);
}

function my_add_polyline(pois) {
	let polyline = new BMap.Polyline(pois, {
		strokeColor: "blue",
		strokeWeight: '1', //折线的宽度，以像素为单位
		strokeOpacity: 0.8, //折线的透明度，取值范围0 - 1
	});
	map.addOverlay(polyline); //增加折线

}

function my_remove_polyline() {
	map.clearOverlays();
}

function moveShip(shipNum, point, rotation) {
	// if (null === ship1.Bc && null === ship2.Bc) {
	// 	init();
	// }
	if (0 === shipNum) {
		ship1.setPosition(point);
		ship1.setRotation(rotation - 90);
	} else if (1 === shipNum) {
		ship2.setPosition(point);
		ship2.setRotation(rotation - 90);
	} else if (2 === shipNum) {
		ship3.setPosition(point);
		ship3.setRotation(rotation - 90);
	} else if (3 === shipNum) {
		ship4.setPosition(point);
		ship4.setRotation(rotation - 90);
	} else if (4 === shipNum) {
		ship0.setPosition(point);
		ship0.setRotation(rotation - 90);
	}

}
