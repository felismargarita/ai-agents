const fs = require('fs')
const index = () => {
  for (let i = 0; i< 10000; i++) {
    fs.appendFileSync('./mock_data.sql', genRow() + '\n')
  }
}

function getRandomDate() {
    // 1. 定义日期范围（注意月份从0开始计数）
    const startDate = new Date(2024, 0, 1);   // 2024年1月1日[1,6](@ref)
    const endDate = new Date(2025, 5, 23);    // 2025年6月23日[4](@ref)
    
    // 2. 转换为时间戳（毫秒数）
    const startTimestamp = startDate.getTime();
    const endTimestamp = endDate.getTime();
    
    // 3. 生成随机时间戳
    const randomTimestamp = Math.random() * (endTimestamp - startTimestamp) + startTimestamp;
    
    // 4. 转换为日期对象
    const randomDate = new Date(randomTimestamp);
    
    // 5. 格式化为YYYY-MM-DD
    const year = randomDate.getFullYear();
    const month = String(randomDate.getMonth() + 1).padStart(2, '0'); // 补零[3](@ref)
    const day = String(randomDate.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}


const random = () => {
  return Math.floor(Math.random() * 10)
}

const genRow = () => {
  const materials = ['硫酸', '硝酸', '磷酸铁锂', '石膏线', '甘油', '石灰石', '硝化甘油', '复写纸','签字笔','工牌套卡']
  // const empNo = ['NO_0001', 'NO_0002', 'NO_0003', 'NO_0004', 'NO_0005']
  
  return `insert into t_inventory (material_name, batch_no, quantity, stock_in_time, stock_in_emp) values ('${materials[random()]}', 'BN_${Math.floor(Math.random() * 1000)}', ${Math.floor(Math.random()* 1000) }, '${getRandomDate()}','NO_${Math.floor(Math.random() * 10000)}' );`
}


index()
