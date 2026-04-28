package com.example.vehiclerental.config;

import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.repository.RentalPriceRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Arrays;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private VehicleTypeRepository vehicleTypeRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private RentalPriceRepository rentalPriceRepository;

    @Override
    public void run(String... args) throws Exception {
        logger.info("开始初始化示例数据...");

        if (vehicleTypeRepository.count() == 0) {
            initVehicleTypes();
            initVehicles();
            initRentalPrices();
            logger.info("示例数据初始化完成！");
        } else {
            logger.info("数据库已存在数据，跳过初始化");
        }
    }

    private void initVehicleTypes() {
        logger.info("初始化车型数据...");

        VehicleType sedan = new VehicleType();
        sedan.setName("经济型轿车");
        sedan.setDescription("适合日常出行，经济实惠");
        sedan.setBasePricePerDay(new BigDecimal("150.00"));
        sedan.setBasePricePerHour(new BigDecimal("20.00"));
        sedan.setAvailable(true);
        vehicleTypeRepository.save(sedan);

        VehicleType suv = new VehicleType();
        suv.setName("SUV");
        suv.setDescription("空间大，适合家庭出行和长途旅行");
        suv.setBasePricePerDay(new BigDecimal("300.00"));
        suv.setBasePricePerHour(new BigDecimal("40.00"));
        suv.setAvailable(true);
        vehicleTypeRepository.save(suv);

        VehicleType luxury = new VehicleType();
        luxury.setName("豪华轿车");
        luxury.setDescription("高端商务用车，尊贵体验");
        luxury.setBasePricePerDay(new BigDecimal("500.00"));
        luxury.setBasePricePerHour(new BigDecimal("80.00"));
        luxury.setAvailable(true);
        vehicleTypeRepository.save(luxury);

        VehicleType van = new VehicleType();
        van.setName("商务车");
        van.setDescription("7座商务车，适合团队出行");
        van.setBasePricePerDay(new BigDecimal("400.00"));
        van.setBasePricePerHour(new BigDecimal("50.00"));
        van.setAvailable(true);
        vehicleTypeRepository.save(van);

        logger.info("车型数据初始化完成，共 {} 种车型", vehicleTypeRepository.count());
    }

    private void initVehicles() {
        logger.info("初始化车辆数据...");

        VehicleType sedan = vehicleTypeRepository.findByName("经济型轿车").orElse(null);
        VehicleType suv = vehicleTypeRepository.findByName("SUV").orElse(null);
        VehicleType luxury = vehicleTypeRepository.findByName("豪华轿车").orElse(null);
        VehicleType van = vehicleTypeRepository.findByName("商务车").orElse(null);

        if (sedan != null) {
            Vehicle v1 = new Vehicle();
            v1.setPlateNumber("京A12345");
            v1.setBrand("丰田");
            v1.setModel("卡罗拉");
            v1.setYear(2022);
            v1.setColor("白色");
            v1.setVehicleType(sedan);
            v1.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v1);

            Vehicle v2 = new Vehicle();
            v2.setPlateNumber("京A67890");
            v2.setBrand("大众");
            v2.setModel("朗逸");
            v2.setYear(2023);
            v2.setColor("黑色");
            v2.setVehicleType(sedan);
            v2.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v2);

            Vehicle v3 = new Vehicle();
            v3.setPlateNumber("京B11111");
            v3.setBrand("日产");
            v3.setModel("轩逸");
            v3.setYear(2021);
            v3.setColor("银色");
            v3.setVehicleType(sedan);
            v3.setStatus(Vehicle.VehicleStatus.MAINTENANCE);
            v3.setRemarks("定期保养中");
            vehicleRepository.save(v3);
        }

        if (suv != null) {
            Vehicle v1 = new Vehicle();
            v1.setPlateNumber("京C22222");
            v1.setBrand("本田");
            v1.setModel("CR-V");
            v1.setYear(2023);
            v1.setColor("黑色");
            v1.setVehicleType(suv);
            v1.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v1);

            Vehicle v2 = new Vehicle();
            v2.setPlateNumber("京C33333");
            v2.setBrand("丰田");
            v2.setModel("RAV4");
            v2.setYear(2022);
            v2.setColor("白色");
            v2.setVehicleType(suv);
            v2.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v2);
        }

        if (luxury != null) {
            Vehicle v1 = new Vehicle();
            v1.setPlateNumber("京D44444");
            v1.setBrand("奔驰");
            v1.setModel("E级");
            v1.setYear(2023);
            v1.setColor("黑色");
            v1.setVehicleType(luxury);
            v1.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v1);

            Vehicle v2 = new Vehicle();
            v2.setPlateNumber("京D55555");
            v2.setBrand("宝马");
            v2.setModel("5系");
            v2.setYear(2022);
            v2.setColor("白色");
            v2.setVehicleType(luxury);
            v2.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v2);
        }

        if (van != null) {
            Vehicle v1 = new Vehicle();
            v1.setPlateNumber("京E66666");
            v1.setBrand("别克");
            v1.setModel("GL8");
            v1.setYear(2023);
            v1.setColor("黑色");
            v1.setVehicleType(van);
            v1.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(v1);
        }

        logger.info("车辆数据初始化完成，共 {} 辆车辆", vehicleRepository.count());
    }

    private void initRentalPrices() {
        logger.info("初始化租赁价格数据...");

        vehicleTypeRepository.findAll().forEach(vehicleType -> {
            RentalPrice price = new RentalPrice();
            price.setVehicleType(vehicleType);
            price.setPricePerDay(vehicleType.getBasePricePerDay());
            price.setPricePerHour(vehicleType.getBasePricePerHour());
            
            BigDecimal pricePerWeek = vehicleType.getBasePricePerDay().multiply(new BigDecimal("6"));
            price.setPricePerWeek(pricePerWeek);
            
            BigDecimal pricePerMonth = vehicleType.getBasePricePerDay().multiply(new BigDecimal("25"));
            price.setPricePerMonth(pricePerMonth);
            
            BigDecimal deposit = vehicleType.getBasePricePerDay().multiply(new BigDecimal("3"));
            price.setDepositAmount(deposit);
            
            price.setActive(true);
            rentalPriceRepository.save(price);
            
            logger.info("为车型 {} 设置价格：日租 {}，周租 {}，月租 {}，押金 {}",
                    vehicleType.getName(), price.getPricePerDay(), price.getPricePerWeek(),
                    price.getPricePerMonth(), price.getDepositAmount());
        });

        logger.info("租赁价格数据初始化完成");
    }
}
