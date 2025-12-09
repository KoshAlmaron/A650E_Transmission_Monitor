from tkinter import *

TPSGrid = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
TempGrid = [-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
DeltaRPMGrid = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]

Configuration = {'LastUsedPort' : ''}

ConfigData = {'AfterChangeMinRPM' :		{'Block': 0, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 3000,	'Step' : 50,	'Name': 'Минимальные'}
			, 'AfterChangeMaxRPM' :		{'Block': 0, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 8000,	'Step' : 50,	'Name': 'Максимальные'}

			, 'IdleTPSLimit' :			{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 10,		'Step' : 1,		'Name': 'Порог ДПДЗ ХХ'}
			, 'MaxSlipRPM' :			{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 5,		'Name': 'Обороты обнаружения проскальзывания'}
			, 'RearGearInitMaxSpeed' :	{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 15,		'Step' : 1,		'Name': 'Порог включения задней передачи'}
			, 'PowerDownMaxTPS' :		{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 100,		'Step' : 1,		'Name': 'Лимит ДПДЗ запроса снижения мощности'}

			, 'MinPressureSLN' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 800,		'Step' : 1,		'Name': 'ШИМ SLN минимального давления'}
			, 'IdlePressureSLN' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 1,		'Name': 'ШИМ простоя SLN'}
			, 'MinPressureSLU' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 1,		'Name': 'Минимальный ШИМ SLU'}

			, 'GlockStartValue' :		{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 400,		'Step' : 1,		'Name': 'Начальный ШИМ SLU'}
			, 'GlockWorkValue' :		{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 800,		'Step' : 1,		'Name': 'Рабочий ШИМ SLU'}
			, 'GlockMaxTPS' :			{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'AdaptationStepRatio' :	{'Block': 4, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 1,	'Max': 2,		'Step' : 1,		'Name': '"Быстрая" адаптация'}

			, 'G2EnableAdaptTPS' :		{'Block': 5, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G2AdaptTPSTempMin' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G2AdaptTPSTempMax' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G2EnableAdaptTemp' :		{'Block': 5, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G2AdaptTempMaxTPS' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'G2EnableAdaptReact' :	{'Block': 6, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G2AdaptReactMinDRPM' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 255,		'Step' : 1,		'Name': 'Минимальное ускорение'}
			, 'G2AdaptReactTempMin' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G2AdaptReactTempMax' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G2EnableAdaptRctTemp' :	{'Block': 6, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G2AdaptRctTempMaxTPS' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}
			, 'G2ReactStepSize' :		{'Block': 6, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 120,		'Step' : 1,		'Name': 'Длительность 1 шага'}

			, 'G3EnableAdaptTPS' :		{'Block': 7, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G3AdaptTPSTempMin' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G3AdaptTPSTempMax' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G3EnableAdaptTemp' :		{'Block': 7, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G3AdaptTempMaxTPS' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'SpeedImpulsPerKM' :		{'Block': 8, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 20000,	'Step' : 1,		'Name': 'Количество импульсов на 1 км'}
			, 'SpeedCalcCoef' :			{'Block': 8, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 300,		'Step' : 1,		'Name': 'Коэффициент для расчета скорости авто'}
}

TablesData = [{'N': 0,	'Menu': 0,	'Table': 'SLTGraph',					'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLT',	'Name': 'SLT - Линейное давление от ДПДЗ'}
			, {'N': 1,	'Menu': 0,	'Table': 'SLTTempCorrGraph',			'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 5,	'Parameter': '',				'Name': 'SLT - Температурная коррекция'}
			, {'N': 2,	'Menu': 0,	'Table': 'SLNGraph',					'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLN',	'Name': 'SLN - Давление подпора гидроаккумуляторов от ДПДЗ'}
			, {'N': 3,	'Menu': 0,	'Table': 'SLNTempCorrGraph',			'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 5,	'Parameter': '',				'Name': 'SLN - Температурная коррекция'}
			, {'N': 4,	'Menu': 1,	'Table': 'SLUGear2Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 500,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': 'SLU G2 - Давление включения второй передачи от ДПДЗ'}
			, {'N': 5,	'Menu': 1,	'Table': 'SLUGear2TPSAdaptGraph',		'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -32,		'Max': 32,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': '    SLU G2 - Адаптация давления включения второй передачи'}
			, {'N': 6,	'Menu': 1,	'Table': 'SLUGear2TempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 5,	'Parameter': '',				'Name': 'SLU G2 - Температурная коррекция давления включения второй передачи'}
			, {'N': 7,	'Menu': 1,	'Table': 'SLUGear2TempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -120,	'Max': 120,		'Step': 5,	'Parameter': '',				'Name': '    SLU G2 - Адаптация температурной коррекции включения второй передачи'}
			, {'N': 8,	'Menu': 1,	'Table': 'GearChangeStepArray',			'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 1,		'Max': 120,		'Step': 5,	'Parameter': '',				'Name': 'SLU G2 - Длительность 1 шага включения передачи'}
			, {'N': 9,	'Menu': 2,	'Table': 'Gear2AdvGraph',				'ArrayX': DeltaRPMGrid,	'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1200,	'Step': 25,	'Parameter': '',				'Name': 'RPM G2 - Опережение по оборотам реативации второй передачи'}
			, {'N': 10,	'Menu': 2,	'Table': 'Gear2AdvAdaptGraph',			'ArrayX': DeltaRPMGrid,	'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': '    RPM G2 - Адаптация оборотов реативации второй передачи'}
			, {'N': 11,	'Menu': 2,	'Table': 'Gear2AdvTempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': 'RPM G2 - Температурная коррекция оборотов реативации второй передачи'}
			, {'N': 12,	'Menu': 2,	'Table': 'Gear2AdvTempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': '    RPM G2 - Адаптация температурной коррекции оборотов реативации второй передачи'}
			, {'N': 13,	'Menu': 3,	'Table': 'SLUGear3Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 500,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': 'SLU G3 - Давление включения третьей передачи от ДПДЗ'}
			, {'N': 14,	'Menu': 3,	'Table': 'SLUGear3DelayGraph',			'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 0,		'Max': 800,		'Step': 20,	'Parameter': '',				'Name': 'SLU G3 - Время удержания от ДПДЗ при включении третьей передачи'}
			, {'N': 15,	'Menu': 3,	'Table': 'SLUGear3TPSAdaptGraph',		'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': '    SLU G3 - Адаптация времени удержания третьей передачи по ДПДЗ'}
			, {'N': 16,	'Menu': 3,	'Table': 'SLUG3DelayTempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': 'SLU G3 - Температурная коррекция времени удержания в мс'}
			, {'N': 17,	'Menu': 3,	'Table': 'SLUGear3TempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': '    SLU G3 - Адаптация времени удержания SLU третьей передачи по температуре в мс'}
			, {'N': 18,	'Menu': 3,	'Table': 'SLNGear3Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLN',	'Name': 'SLN G3 - Давление SLN включения третьей передачи от ДПДЗ'}
			, {'N': 19,	'Menu': 3,	'Table': 'SLNGear3OffsetGraph',			'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -1000,	'Max': 1000,	'Step': 20,	'Parameter': '',				'Name': 'SLN G3 - Смещение времени активации SLN при включении третьей передачи'}
			, {'N': 20,	'Menu': 4,	'Table': 'TPSGraph',					'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1023,	'Step': 4,	'Parameter': '',				'Name': 'ДПДЗ (показания АЦП)'}
			, {'N': 21,	'Menu': 4,	'Table': 'OilTempGraph',				'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1023,	'Step': 4,	'Parameter': '',				'Name': 'Температура масла (показания АЦП)'}
			, {'N': 22,	'Menu': 5,	'Table': 'GearSpeedGraphs',				'ArrayX': TPSGrid,		'Type': 'uint8_t',	'Size' : 0,	'Min': 0,		'Max': 150,		'Step': 1,	'Parameter': '',				'Name': 'Графики переключений передач'}
]

VariableSize = {'int8_t' : 1
				, 'uint8_t' : 1
				, 'int16_t' : 2
				, 'uint16_t' : 2
}

for Table in TablesData:
	Table['Size'] = len(Table['ArrayX']) * VariableSize[Table['Type']]
	if Table['Table'] == 'GearSpeedGraphs':
		Table['Size'] *= 8

# Список таблиц с командами, для которых есть адапатация.
ApplyAdaptationCommands = {	'SLUGear2Graph':				'APPLY_G2_TPS_ADAPT_COMMAND'
							, 'SLUGear2TempCorrGraph':		'APPLY_G2_TEMP_ADAPT_COMMAND'
							, 'Gear2AdvGraph':				'APPLY_G2_ADV_ADAPT_COMMAND'
							, 'Gear2AdvTempCorrGraph' :		'APPLY_G2_ADV_TEMP_ADAPT_COMMAND'
							, 'SLUGear3DelayGraph':			'APPLY_G3_TPS_ADAPT_COMMAND'
							, 'SLUG3DelayTempCorrGraph':	'APPLY_G3_TEMP_ADAPT_COMMAND'
}

ArduinoPins = {
		' 0': {'Port': 'PE0', 'Functions': 'RX0', 'State': 0},
		' 1': {'Port': 'PE1', 'Functions': 'TX0', 'State': 0},
		' 2': {'Port': 'PE4', 'Functions': 'OC3B, INT4', 'State': 0},
		' 3': {'Port': 'PE5', 'Functions': 'OC3C, INT5', 'State': 0},
		' 4': {'Port': 'PG5', 'Functions': 'OC0B', 'State': 0},
		' 5': {'Port': 'PE3', 'Functions': 'OC3A', 'State': 0},
		' 6': {'Port': 'PH3', 'Functions': 'OC4A', 'State': 0},
		' 7': {'Port': 'PH4', 'Functions': 'OC4B', 'State': 0},
		' 8': {'Port': 'PH5', 'Functions': 'OC4C', 'State': 0},
		' 9': {'Port': 'PH6', 'Functions': 'OC2B', 'State': 0},
		'10': {'Port': 'PB4', 'Functions': 'OC2A', 'State': 0},
		'11': {'Port': 'PB5', 'Functions': 'OC1A', 'State': 0},
		'12': {'Port': 'PB6', 'Functions': 'OC1B', 'State': 0},
		'13': {'Port': 'PB7', 'Functions': 'OC1C', 'State': 0},
		'14': {'Port': 'PJ1', 'Functions': 'TX3', 'State': 0},
		'15': {'Port': 'PJ0', 'Functions': 'RX3', 'State': 0},
		'16': {'Port': 'PH1', 'Functions': 'TX2', 'State': 0},
		'17': {'Port': 'PH0', 'Functions': 'RX2', 'State': 0},
		'18': {'Port': 'PD3', 'Functions': 'TX1, INT3', 'State': 0},
		'19': {'Port': 'PD2', 'Functions': 'RX1, INT2', 'State': 0},
		'20': {'Port': 'PD1', 'Functions': 'SDA, INT1', 'State': 0},
		'21': {'Port': 'PD0', 'Functions': 'SCL, INT0', 'State': 0},
		'22': {'Port': 'PA0', 'Functions': '', 'State': 0},
		'23': {'Port': 'PA1', 'Functions': '', 'State': 0},
		'24': {'Port': 'PA2', 'Functions': '', 'State': 0},
		'25': {'Port': 'PA3', 'Functions': '', 'State': 0},
		'26': {'Port': 'PA4', 'Functions': '', 'State': 0},
		'27': {'Port': 'PA5', 'Functions': '', 'State': 0},
		'28': {'Port': 'PA6', 'Functions': '', 'State': 0},
		'29': {'Port': 'PA7', 'Functions': '', 'State': 0},
		'30': {'Port': 'PC7', 'Functions': '', 'State': 0},
		'31': {'Port': 'PC6', 'Functions': '', 'State': 0},
		'32': {'Port': 'PC5', 'Functions': '', 'State': 0},
		'33': {'Port': 'PC4', 'Functions': '', 'State': 0},
		'34': {'Port': 'PC3', 'Functions': '', 'State': 0},
		'35': {'Port': 'PC2', 'Functions': '', 'State': 0},
		'36': {'Port': 'PC1', 'Functions': '', 'State': 0},
		'37': {'Port': 'PC0', 'Functions': '', 'State': 0},
		'38': {'Port': 'PD7', 'Functions': '', 'State': 0},
		'39': {'Port': 'PG2', 'Functions': '', 'State': 0},
		'40': {'Port': 'PG1', 'Functions': '', 'State': 0},
		'41': {'Port': 'PG0', 'Functions': '', 'State': 0},
		'42': {'Port': 'PL7', 'Functions': '', 'State': 0},
		'43': {'Port': 'PL6', 'Functions': '', 'State': 0},
		'44': {'Port': 'PL5', 'Functions': 'OC5C', 'State': 0},
		'45': {'Port': 'PL4', 'Functions': 'OC5B', 'State': 0},
		'46': {'Port': 'PL3', 'Functions': 'OC5A', 'State': 0},
		'47': {'Port': 'PL2', 'Functions': '', 'State': 0},
		'48': {'Port': 'PL1', 'Functions': 'ICP5', 'State': 0},
		'49': {'Port': 'PL0', 'Functions': 'ICP4', 'State': 0},
		'50': {'Port': 'PB3', 'Functions': 'MISO', 'State': 0},
		'51': {'Port': 'PB2', 'Functions': 'MOSI', 'State': 0},
		'52': {'Port': 'PB1', 'Functions': 'SCK', 'State': 0},
		'53': {'Port': 'PB0', 'Functions': 'SS', 'State': 0},
		'A0': {'Port': 'PF0', 'Functions': 'ADC0', 'State': 0},
		'A1': {'Port': 'PF1', 'Functions': 'ADC1', 'State': 0},
		'A2': {'Port': 'PF2', 'Functions': 'ADC2', 'State': 0},
		'A3': {'Port': 'PF3', 'Functions': 'ADC3', 'State': 0},
		'A4': {'Port': 'PF4', 'Functions': 'ADC4', 'State': 0},
		'A5': {'Port': 'PF5', 'Functions': 'ADC5', 'State': 0},
		'A6': {'Port': 'PF6', 'Functions': 'ADC6', 'State': 0},
		'A7': {'Port': 'PF7', 'Functions': 'ADC7', 'State': 0},
		'A8': {'Port': 'PK0', 'Functions': 'ADC8', 'State': 0},
		'A9': {'Port': 'PK1', 'Functions': 'ADC9', 'State': 0},
		'A10': {'Port': 'PK2', 'Functions': 'ADC10', 'State': 0},
		'A11': {'Port': 'PK3', 'Functions': 'ADC11', 'State': 0},
		'A12': {'Port': 'PK4', 'Functions': 'ADC12', 'State': 0},
		'A13': {'Port': 'PK5', 'Functions': 'ADC13', 'State': 0},
		'A14': {'Port': 'PK6', 'Functions': 'ADC14', 'State': 0},
		'A15': {'Port': 'PK7', 'Functions': 'ADC15', 'State': 0},
}