// Echarts树 结点点击事件
ec_tree.on('click', function (params) {
	// 控制台打印数据的名称
	$('#dataId').attr('value', params.value);
	var vmid = params.value;

	getVMData(vmid);


});

// ec_tree.on('dblclick', (e) => {
// 	const name = e.data.name;
// 	const curNode = ec_tree._chartsViews[0]._data.tree._nodes.find(item => {
// 		return item.name === name;
// 	});
// 	const depth = curNode.depth;
// 	const curIsExpand = curNode.isExpand;
// 	ec_tree._chartsViews[0]._data.tree._nodes.forEach((item, index) => {
// 		if (item.depth === depth && item.name !== name && !curIsExpand) {
// 			item.isExpand = false;
// 		}
// 	});
// })


// 清除绘图 按钮点击事件
$("#clearPolyline").click(function (event) {
	// alert("clear polyline")
	map.clearOverlays();
	init() //初始化船的图片
	ec_tree.setOption(ec_tree_option);
	//$('#voImg').attr('src', "../static/res/Figure1.png");
});

// // 测试动态更新VO图 点击事件
// $("#testDynamicImg").click(function (event) {
// 	updateVoImg("1000010086312797");
// });


// 获取最新仿真树
$("#getSimTree").click(function (event) {
	// 先清理掉当前的绘图PolyLine
	// map.clearOverlays();
	// var treeid = "Tree2004022208017821";
	// var treeid = "Tree2004022316511498";
	// treeUrl = "/tree/" + treeid;

	init() //初始化船的图片

	lastestTreeUrl = "/tree/lastest";
	$.ajax('', {
		url: lastestTreeUrl,
		dataType: "json",
		success: function (data) {
			ec_tree_option.series[0].data = data.TREEData.data;
			ec_tree.setOption(ec_tree_option);
			// 将TREEID填写到treeId输入框中
			$('#treeId').attr('value', data.TREEID);
		},
		error: function (xhr, type, errorThrown) {
			alert(error);
		}
	});
});

// 动画功能
function animation(SimData) {
	let timeOut = 0;
	let pointSize = 10;
	// let shipVOImg = new Array(); // 用于保存主船的VOImdID

	// // VOImg 相关
	// for (let moment = 0; moment < SimData.length - 1; moment++) {
	// 	if (SimData[moment][0].VOImgID) {
	// 		shipVOImg.push(SimData[moment][0].VOImgID);
	// 	} else {
	// 		shipVOImg.push('figure');
	// 	}
	// }

	for (let moment = 0; moment < SimData.length - 1; moment++) {
		let fromInfo = SimData[moment];
		let toInfo = SimData[moment + 1];
		let shipNum = fromInfo.length;
		if (shipNum > 0) {
			let shipPointList = [];
			let rotationList = [];
			// 把船每一次前进分成pointSize步，存入shipPointList；方向存入rotationList
			for (let ship = 0; ship < shipNum; ship++) {
				let lonStep = (toInfo[ship].lon - fromInfo[ship].lon) / pointSize;
				let latStep = (toInfo[ship].lat - fromInfo[ship].lat) / pointSize;
				let pointList = [];
				let rotation = toInfo[ship].heading;
				rotationList.push(rotation);
				for (let i = 0; i < pointSize; i++) {
					let p = new BMap.Point(fromInfo[ship].lon + i * lonStep, fromInfo[ship].lat + i * latStep);
					pointList.push(p);
				}
				shipPointList.push(pointList);
			}
			//船
			for (let i = 0; i < pointSize - 1; i++) {
				for (let ship = 0; ship < shipNum; ship++) {
					(function (ship, pointList, timeOut, i, rotation) {
						setTimeout(() => {
							moveShip(ship, pointList[i + 1], rotation);
							my_add_polyline([pointList[i], pointList[i + 1]]);
						}, timeOut);
					})(ship, shipPointList[ship], timeOut, i, rotationList[ship])
					// pointList = shipPointList[ship]
					// rotation = rotationList[ship]
					// moveShip(ship, pointList[i + 1], rotation);
					// my_add_polyline([pointList[i], pointList[i + 1]]);
				}
			}
			// updateVoImg(shipVOImg[moment]);
		}
	}
}

// // 更新VO图功能函数
// function updateVoImg(imgName) {
// 	console.log("imgName: ", imgName)
// 	// imgName: String
// 	// imgUrl = "/img/"+ imgName.toString();

// 	// TODO: 有毒！！！
// 	// imgUrl = "/vm/2004071252277034";
// 	imgUrl = "/img/" + imgName;
// 	// 方式1：DOM操作img 属性
// 	// $('#voImg').attr('src', imgUrl);

// 	// 方式2 Ajax方式
// 	$.ajax('', {
// 		url: imgUrl,
// 		success: function (data) {
// 			// console.log("前端调用测试data:", data)
// 			$('#voImg').attr('src', "data:image/png;base64," + data);
// 		},
// 		error: function (xhr, type, errorThrown) {
// 			alert("error");
// 		}
// 	});
// }

// 输入VMID，绘制PolyLine
function getVMData(VMID) {
	vmUrl = "/vm/" + VMID.toString();
	$.ajax('', {
		url: vmUrl,
		dataType: "json",
		success: function (data) {
			let SimData = data.SimData;
			//显示概率
			$('#vmprob').attr('value', data.VM_prob);
			// init()
			animation(SimData);
		},
		error: function (xhr, type, errorThrown) {
			console.log(error)
		}
	});
}