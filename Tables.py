
TPSGrid = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
TempGrid = [-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
DeltaRPMGrid = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]

ConfigData = {'AfterChangeMinRPM' :		{'Block': 0, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 3000,	'Step' : 50,	'Name': 'Минимальные'}
			, 'AfterChangeMaxRPM' :		{'Block': 0, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 8000,	'Step' : 50,	'Name': 'Максимальные'}

			, 'IdleTPSLimit' :			{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 10,		'Step' : 1,		'Name': 'Порог ДПДЗ ХХ'}
			, 'MaxSlipRPM' :			{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 5,		'Name': 'Обороты обнаружения проскальзывания'}
			, 'RearGearInitMaxSpeed' :	{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 15,		'Step' : 1,		'Name': 'Пророг включения задней передачи'}
			, 'PowerDownMaxTPS' :		{'Block': 1, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 100,		'Step' : 1,		'Name': 'Лимит ДПДЗ запроса снижения мощности'}

			, 'MinPressureSLN' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 800,		'Step' : 1,		'Name': 'ШИМ SLN минимального давления'}
			, 'IdlePressureSLN' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 1,		'Name': 'ШИМ простоя SLN'}
			, 'MinPressureSLU' :		{'Block': 2, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 150,		'Step' : 1,		'Name': 'Минимальный ШИМ SLU'}

			, 'GlockStartValue' :		{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 400,		'Step' : 1,		'Name': 'Начальный ШИМ SLU'}
			, 'GlockWorkValue' :		{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 800,		'Step' : 1,		'Name': 'Рабочий ШИМ SLU'}
			, 'GlockMaxTPS' :			{'Block': 3, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'AdaptationStepRatio' :	{'Block': 4, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 1,	'Max': 2,		'Step' : 1,		'Name': '"Быстрая" адаптация'}

			, 'G2EnableAdaptTPS' :		{'Block': 5, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G2AdaptTPSTempMin' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G2AdaptTPSTempMax' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G2EnableAdaptTemp' :		{'Block': 5, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G2AdaptTempMaxTPS' :		{'Block': 5, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'G2EnableAdaptReact' :	{'Block': 6, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G2AdaptReactMinDRPM' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 255,		'Step' : 1,		'Name': 'Минимальное ускорение'}
			, 'G2AdaptReactTempMin' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G2AdaptReactTempMax' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G2EnableAdaptRctTemp' :	{'Block': 6, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G2AdaptRctTempMaxTPS' :	{'Block': 6, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'G3EnableAdaptTPS' :		{'Block': 7, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по ДПДЗ'}
			, 'G3AdaptTPSTempMin' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Минимальная температура'}
			, 'G3AdaptTPSTempMax' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'int8_t',	'Value': None, 'Min': 0,	'Max': 80,		'Step' : 1,		'Name': 'Максимальная температура'}
			, 'G3EnableAdaptTemp' :		{'Block': 7, 'Element' : 'CheckButton',	'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 1,		'Step' : 1,		'Name': 'Адаптация по температуре'}
			, 'G3AdaptTempMaxTPS' :		{'Block': 7, 'Element' : 'Spinbox',		'Type': 'uint8_t',	'Value': None, 'Min': 0,	'Max': 50,		'Step' : 1,		'Name': 'Лимит ДПДЗ'}

			, 'SpeedImpulsPerKM' :		{'Block': 8, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 20000,	'Step' : 1,		'Name': 'Количество импульсов на 1 км'}
			, 'SpeedCalcCoef' :			{'Block': 8, 'Element' : 'Spinbox',		'Type': 'uint16_t',	'Value': None, 'Min': 0,	'Max': 300,		'Step' : 1,		'Name': 'Коэффициент для расчета скорости авто'}
}

TablesData = [{'N': 0,  'Table': 'SLTGraph',					'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLT',	'Name': 'SLT - Линейное давление от ДПДЗ'}
			, {'N': 1,  'Table': 'SLTTempCorrGraph',			'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 5,	'Parameter': '',				'Name': 'SLT - Температурная коррекция'}
			, {'N': 2,  'Table': 'SLNGraph',					'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLN',	'Name': 'SLN - Давление  от ДПДЗ (величина сброса давления)'}
			, {'N': 3,  'Table': 'SLUGear2Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 500,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': 'SLU G2 - Давление включения второй передачи от ДПДЗ'}
			, {'N': 4,  'Table': 'SLUGear2TPSAdaptGraph',		'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -32,		'Max': 32,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': '    Адаптация давления включения второй передачи'}
			, {'N': 5,  'Table': 'SLUGear2TempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 5,	'Parameter': '',				'Name': 'SLU G2 - Температурная коррекция давления включения второй передачи'}
			, {'N': 6,  'Table': 'SLUGear2TempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -120,	'Max': 120,		'Step': 5,	'Parameter': '',				'Name': '    Адаптация температурной коррекции включения второй передачи'}
			, {'N': 7,  'Table': 'Gear2AdvGraph',				'ArrayX': DeltaRPMGrid,	'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1000,	'Step': 25,	'Parameter': '',				'Name': 'RPM G2 - Опережение по оборотам реативации второй передачи'}
			, {'N': 8,  'Table': 'Gear2AdvAdaptGraph',			'ArrayX': DeltaRPMGrid,	'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': '    Адаптация оборотов реативации второй передачи'}
			, {'N': 9,  'Table': 'Gear2AdvTempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': 'RPM G2 - Температурная коррекция оборотов реативации второй передачи'}
			, {'N': 10, 'Table': 'Gear2AdvTempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -300,	'Max': 300,		'Step': 25,	'Parameter': '',				'Name': '    Адаптация температурной коррекции оборотов реативации второй передачи'}
			, {'N': 11, 'Table': 'SLUGear3Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 500,		'Step': 4,	'Parameter': 'GearChangeSLU',	'Name': 'SLU G3 - Давление включения третьей передачи от ДПДЗ'}
			, {'N': 12, 'Table': 'SLUGear3DelayGraph',			'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 0,		'Max': 800,		'Step': 20,	'Parameter': '',				'Name': 'SLU G3 - Время удержания от ДПДЗ при включении третьей передачи'}
			, {'N': 13, 'Table': 'SLUGear3TPSAdaptGraph',		'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': '    SLU G3 - Адаптация времени удержания третьей передачи по ДПДЗ в мс'}
			, {'N': 14, 'Table': 'SLUG3DelayTempCorrGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': 'SLU G3 - Температурная коррекция времени удержания в мс'}
			, {'N': 15, 'Table': 'SLUGear3TempAdaptGraph',		'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -200,	'Max': 200,		'Step': 20,	'Parameter': '',				'Name': '    SLU G3 - Адаптация времени удержания SLU третьей передачи по температуре в мс'}
			, {'N': 16, 'Table': 'SLNGear3Graph',				'ArrayX': TPSGrid,		'Type': 'uint16_t',	'Size' : 0,	'Min': 100,		'Max': 800,		'Step': 4,	'Parameter': 'GearChangeSLN',	'Name': 'SLN G3 - Давление SLN включения третьей передачи от ДПДЗ'}
			, {'N': 17, 'Table': 'SLNGear3OffsetGraph',			'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': -1000,	'Max': 1000,	'Step': 20,	'Parameter': '',				'Name': 'SLN G3 - Смещение времени включения SLN при включении третьей передачи'}
			, {'N': 18, 'Table': 'TPSGraph',					'ArrayX': TPSGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1023,	'Step': 4,	'Parameter': '',				'Name': 'ДПДЗ (показания АЦП)'}
			, {'N': 19, 'Table': 'OilTempGraph',				'ArrayX': TempGrid,		'Type': 'int16_t',	'Size' : 0,	'Min': 0,		'Max': 1023,	'Step': 4,	'Parameter': '',				'Name': 'Температура масла (показания АЦП)'}
			, {'N': 20, 'Table': 'GearSpeedGraphs',				'ArrayX': TPSGrid,		'Type': 'uint8_t',	'Size' : 0,	'Min': 0,		'Max': 150,		'Step': 1,	'Parameter': '',				'Name': 'Скорости переключения передач'}
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