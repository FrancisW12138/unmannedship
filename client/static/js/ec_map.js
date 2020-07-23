// 用echarts实现map，此方案已弃用，改用百度地图，见my_bmap.js
var ec_map = echarts.init(document.getElementById('map'));

// var my_map_data = // 从 3.2.0 起改为如下配置
// 	{
// 		coords: [
// 			[122.226654, 31.210672], // 起点
// 			[122.226660, 31.210660] // 终点
// 			// 	//... // 如果 polyline 为 true 还可以设置更多的点
// 		],
// 		// 统一的样式设置
// 		// lineStyle: {

// 		// }
// 	}

var my_map_data = [
	[{
		"coord": [122.226654, 31.210672],
		// "elevation": 21
	}, {
		"coord": [122.326654, 31.310672],
		// "elevation": 5
	},{
		"coord": [123.326654, 31.410672],
		// "elevation": 5
	},{
		"coord": [122.526654, 31.510672],
		// "elevation": 5
	}],
]




var ec_map_option = {
	bmap: {
		// center: [111.010842,30.837771], // 三峡水域
		center: [122.226654, 31.210672], // 上海附近开阔水域
		zoom: 10,
		roam: true,

	},

	series: [{
		type: 'lines',
		coordinateSystem: 'bmap',
		data: my_map_data,
		polyline: true,
		lineStyle: {
			color: 'red',
			opacity: 1,
			width: 2
		},
		markPoint: {
				 symbol: 'circle', 
		},
	}]
}

 

ec_map.setOption(ec_map_option)
