package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.RentalOrderRepository;
import com.example.vehiclerental.repository.RentalPriceRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;

@Service
public class RentalOrderService {

    private static final Logger logger = LoggerFactory.getLogger(RentalOrderService.class);
    
    private static final Pattern PHONE_PATTERN = Pattern.compile("^1[3-9]\\d{9}$");

    @Autowired
    private RentalOrderRepository rentalOrderRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private RentalPriceRepository rentalPriceRepository;

    @Transactional
    public RentalOrder createRentalOrder(RentalOrder rentalOrder, Long vehicleId) {
        logger.info("开始创建租赁订单，车辆ID: {}, 客户姓名: {}", vehicleId, rentalOrder.getCustomerName());

        Vehicle vehicle = vehicleRepository.findById(vehicleId)
                .orElseThrow(() -> {
                    logger.error("车辆不存在，ID: {}", vehicleId);
                    return new ResourceNotFoundException("车辆", "id", vehicleId);
                });

        if (vehicle.getStatus() != Vehicle.VehicleStatus.AVAILABLE) {
            logger.warn("车辆 {} 当前不可租赁，状态: {}", vehicle.getPlateNumber(), vehicle.getStatus());
            throw new BusinessException("该车辆当前不可租赁，状态: " + vehicle.getStatus());
        }

        if (!isValidPhoneNumber(rentalOrder.getCustomerPhone())) {
            logger.warn("客户手机号格式无效: {}", rentalOrder.getCustomerPhone());
            throw new BusinessException("请输入有效的11位手机号码");
        }

        LocalDateTime now = LocalDateTime.now();
        if (rentalOrder.getPickupTime().isBefore(now)) {
            logger.warn("取车时间早于当前时间，取车时间: {}, 当前时间: {}", rentalOrder.getPickupTime(), now);
            throw new BusinessException("取车时间不能早于当前时间");
        }

        if (rentalOrder.getPickupTime().isAfter(rentalOrder.getReturnTime())) {
            logger.warn("取车时间晚于还车时间");
            throw new BusinessException("取车时间不能晚于还车时间");
        }

        List<RentalOrder.OrderStatus> activeStatuses = Arrays.asList(
                RentalOrder.OrderStatus.PENDING,
                RentalOrder.OrderStatus.CONFIRMED,
                RentalOrder.OrderStatus.ACTIVE
        );
        
        List<RentalOrder> overlappingOrders = rentalOrderRepository.findOverlappingOrders(
                vehicle,
                rentalOrder.getPickupTime(),
                rentalOrder.getReturnTime(),
                activeStatuses
        );
        
        if (!overlappingOrders.isEmpty()) {
            logger.warn("车辆 {} 在时间段 {} 至 {} 内已有预约或正在租赁中", 
                    vehicle.getPlateNumber(), rentalOrder.getPickupTime(), rentalOrder.getReturnTime());
            throw new BusinessException("该车辆在选定时间段内已有预约或正在租赁中");
        }

        VehicleType vehicleType = vehicle.getVehicleType();
        RentalPrice price = getActivePrice(vehicleType, rentalOrder.getPickupTime());
        
        if (price != null) {
            rentalOrder.setUnitPrice(getUnitPrice(price, rentalOrder.getRentalUnit()));
            rentalOrder.setDepositAmount(price.getDepositAmount());
            logger.debug("使用租赁价格配置: 单价={}, 押金={}", rentalOrder.getUnitPrice(), rentalOrder.getDepositAmount());
        } else {
            rentalOrder.setUnitPrice(vehicleType.getBasePricePerDay());
            logger.debug("使用车型基础价格: {}", vehicleType.getBasePricePerDay());
        }

        BigDecimal totalAmount = calculateTotalAmount(
                rentalOrder.getUnitPrice(),
                rentalOrder.getRentalUnit(),
                rentalOrder.getPickupTime(),
                rentalOrder.getReturnTime()
        );
        rentalOrder.setTotalAmount(totalAmount);
        logger.info("计算租赁总金额: {}", totalAmount);

        rentalOrder.setVehicle(vehicle);
        rentalOrder.setOrderNumber(generateOrderNumber());
        rentalOrder.setStatus(RentalOrder.OrderStatus.PENDING);

        RentalOrder savedOrder = rentalOrderRepository.save(rentalOrder);
        logger.info("租赁订单创建成功，订单号: {}, 总金额: {}", savedOrder.getOrderNumber(), savedOrder.getTotalAmount());
        return savedOrder;
    }

    public List<RentalOrder> getAllRentalOrders() {
        return rentalOrderRepository.findAll();
    }

    public RentalOrder getRentalOrderById(Long id) {
        return rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));
    }

    public RentalOrder getRentalOrderByOrderNumber(String orderNumber) {
        return rentalOrderRepository.findByOrderNumber(orderNumber)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "订单号", orderNumber));
    }

    @Transactional
    public RentalOrder updateRentalOrder(Long id, RentalOrder orderDetails) {
        RentalOrder rentalOrder = rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));

        if (rentalOrder.getStatus() == RentalOrder.OrderStatus.COMPLETED ||
            rentalOrder.getStatus() == RentalOrder.OrderStatus.CANCELLED) {
            logger.warn("尝试修改已完成或已取消的订单，订单ID: {}", id);
            throw new BusinessException("已完成或已取消的订单无法修改");
        }

        if (orderDetails.getCustomerPhone() != null && !isValidPhoneNumber(orderDetails.getCustomerPhone())) {
            logger.warn("修改订单时手机号格式无效: {}", orderDetails.getCustomerPhone());
            throw new BusinessException("请输入有效的11位手机号码");
        }

        if (orderDetails.getPickupTime() != null && orderDetails.getReturnTime() != null) {
            LocalDateTime now = LocalDateTime.now();
            if (orderDetails.getPickupTime().isBefore(now)) {
                logger.warn("修改订单时取车时间早于当前时间");
                throw new BusinessException("取车时间不能早于当前时间");
            }

            if (orderDetails.getPickupTime().isAfter(orderDetails.getReturnTime())) {
                throw new BusinessException("取车时间不能晚于还车时间");
            }

            Vehicle vehicle = rentalOrder.getVehicle();
            List<RentalOrder.OrderStatus> activeStatuses = Arrays.asList(
                    RentalOrder.OrderStatus.PENDING,
                    RentalOrder.OrderStatus.CONFIRMED,
                    RentalOrder.OrderStatus.ACTIVE
            );

            List<RentalOrder> overlappingOrders = rentalOrderRepository.findOverlappingOrders(
                    vehicle,
                    orderDetails.getPickupTime(),
                    orderDetails.getReturnTime(),
                    activeStatuses
            );

            overlappingOrders.removeIf(o -> o.getId().equals(id));

            if (!overlappingOrders.isEmpty()) {
                throw new BusinessException("该车辆在选定时间段内已有预约或正在租赁中");
            }

            rentalOrder.setPickupTime(orderDetails.getPickupTime());
            rentalOrder.setReturnTime(orderDetails.getReturnTime());

            BigDecimal totalAmount = calculateTotalAmount(
                    rentalOrder.getUnitPrice(),
                    rentalOrder.getRentalUnit(),
                    orderDetails.getPickupTime(),
                    orderDetails.getReturnTime()
            );
            rentalOrder.setTotalAmount(totalAmount);
            logger.info("更新订单 {} 的租赁时间，重新计算金额: {}", id, totalAmount);
        }

        if (orderDetails.getCustomerName() != null) {
            rentalOrder.setCustomerName(orderDetails.getCustomerName());
        }
        if (orderDetails.getCustomerPhone() != null) {
            rentalOrder.setCustomerPhone(orderDetails.getCustomerPhone());
        }
        if (orderDetails.getCustomerIdCard() != null) {
            rentalOrder.setCustomerIdCard(orderDetails.getCustomerIdCard());
        }
        if (orderDetails.getPickupLocation() != null) {
            rentalOrder.setPickupLocation(orderDetails.getPickupLocation());
        }
        if (orderDetails.getReturnLocation() != null) {
            rentalOrder.setReturnLocation(orderDetails.getReturnLocation());
        }
        if (orderDetails.getRemarks() != null) {
            rentalOrder.setRemarks(orderDetails.getRemarks());
        }
        if (orderDetails.getDepositAmount() != null) {
            rentalOrder.setDepositAmount(orderDetails.getDepositAmount());
        }

        return rentalOrderRepository.save(rentalOrder);
    }

    @Transactional
    public RentalOrder confirmOrder(Long id) {
        RentalOrder rentalOrder = rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));

        if (rentalOrder.getStatus() != RentalOrder.OrderStatus.PENDING) {
            logger.warn("尝试确认非待确认状态的订单，订单ID: {}, 状态: {}", id, rentalOrder.getStatus());
            throw new BusinessException("只有待确认的订单可以确认");
        }

        rentalOrder.setStatus(RentalOrder.OrderStatus.CONFIRMED);
        RentalOrder savedOrder = rentalOrderRepository.save(rentalOrder);
        logger.info("订单 {} 已确认", savedOrder.getOrderNumber());
        return savedOrder;
    }

    @Transactional
    public RentalOrder startRental(Long id) {
        RentalOrder rentalOrder = rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));

        if (rentalOrder.getStatus() != RentalOrder.OrderStatus.CONFIRMED) {
            logger.warn("尝试开始非已确认状态的订单，订单ID: {}, 状态: {}", id, rentalOrder.getStatus());
            throw new BusinessException("只有已确认的订单可以开始租赁");
        }

        Vehicle vehicle = rentalOrder.getVehicle();
        vehicle.setStatus(Vehicle.VehicleStatus.RENTED);
        vehicleRepository.save(vehicle);

        rentalOrder.setStatus(RentalOrder.OrderStatus.ACTIVE);
        RentalOrder savedOrder = rentalOrderRepository.save(rentalOrder);
        logger.info("订单 {} 开始租赁，车辆 {} 状态更新为已出租", 
                savedOrder.getOrderNumber(), vehicle.getPlateNumber());
        return savedOrder;
    }

    @Transactional
    public RentalOrder completeRental(Long id) {
        RentalOrder rentalOrder = rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));

        if (rentalOrder.getStatus() != RentalOrder.OrderStatus.ACTIVE) {
            logger.warn("尝试完成非进行中状态的订单，订单ID: {}, 状态: {}", id, rentalOrder.getStatus());
            throw new BusinessException("只有进行中的订单可以完成");
        }

        Vehicle vehicle = rentalOrder.getVehicle();
        vehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);
        vehicleRepository.save(vehicle);

        rentalOrder.setActualReturnTime(LocalDateTime.now());
        rentalOrder.setStatus(RentalOrder.OrderStatus.COMPLETED);

        BigDecimal extraCharge = calculateExtraCharge(rentalOrder);
        if (extraCharge.compareTo(BigDecimal.ZERO) > 0) {
            rentalOrder.setExtraCharge(extraCharge);
            rentalOrder.setTotalAmount(rentalOrder.getTotalAmount().add(extraCharge));
            logger.info("订单 {} 产生额外费用: {}", rentalOrder.getOrderNumber(), extraCharge);
        }

        RentalOrder savedOrder = rentalOrderRepository.save(rentalOrder);
        logger.info("订单 {} 已完成，总金额: {}", savedOrder.getOrderNumber(), savedOrder.getTotalAmount());
        return savedOrder;
    }

    @Transactional
    public RentalOrder cancelOrder(Long id, String cancelReason) {
        RentalOrder rentalOrder = rentalOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁订单", "id", id));

        if (rentalOrder.getStatus() == RentalOrder.OrderStatus.COMPLETED) {
            logger.warn("尝试取消已完成的订单，订单ID: {}", id);
            throw new BusinessException("已完成的订单无法取消");
        }

        if (rentalOrder.getStatus() == RentalOrder.OrderStatus.ACTIVE) {
            Vehicle vehicle = rentalOrder.getVehicle();
            vehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);
            vehicleRepository.save(vehicle);
            logger.info("订单 {} 取消，车辆 {} 状态更新为可用", 
                    rentalOrder.getOrderNumber(), vehicle.getPlateNumber());
        }

        rentalOrder.setStatus(RentalOrder.OrderStatus.CANCELLED);
        rentalOrder.setCancelReason(cancelReason);
        
        RentalOrder savedOrder = rentalOrderRepository.save(rentalOrder);
        logger.info("订单 {} 已取消，取消原因: {}", savedOrder.getOrderNumber(), cancelReason);
        return savedOrder;
    }

    public List<RentalOrder> getOrdersByStatus(RentalOrder.OrderStatus status) {
        return rentalOrderRepository.findByStatus(status);
    }

    public List<RentalOrder> getOrdersByCustomerName(String customerName) {
        return rentalOrderRepository.findByCustomerNameContaining(customerName);
    }

    public List<RentalOrder> getOrdersByVehicle(Long vehicleId) {
        Vehicle vehicle = vehicleRepository.findById(vehicleId)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "id", vehicleId));
        return rentalOrderRepository.findByVehicle(vehicle);
    }

    public List<RentalOrder> getOrdersByPickupTimeRange(LocalDateTime start, LocalDateTime end) {
        return rentalOrderRepository.findByPickupTimeBetween(start, end);
    }

    public List<RentalOrder> getOrdersByActualReturnTimeRange(LocalDateTime start, LocalDateTime end) {
        return rentalOrderRepository.findByActualReturnTimeBetween(start, end);
    }

    private boolean isValidPhoneNumber(String phone) {
        if (phone == null) {
            return false;
        }
        String cleanPhone = phone.replaceAll("\\s|-", "");
        return PHONE_PATTERN.matcher(cleanPhone).matches();
    }

    private RentalPrice getActivePrice(VehicleType vehicleType, LocalDateTime date) {
        List<RentalPrice> prices = rentalPriceRepository.findActivePricesForDate(vehicleType, date);
        return prices.isEmpty() ? null : prices.get(0);
    }

    private BigDecimal getUnitPrice(RentalPrice price, RentalOrder.RentalUnit unit) {
        switch (unit) {
            case HOUR:
                return price.getPricePerHour() != null ? price.getPricePerHour() : BigDecimal.ZERO;
            case DAY:
                return price.getPricePerDay() != null ? price.getPricePerDay() : BigDecimal.ZERO;
            case WEEK:
                return price.getPricePerWeek() != null ? price.getPricePerWeek() : BigDecimal.ZERO;
            case MONTH:
                return price.getPricePerMonth() != null ? price.getPricePerMonth() : BigDecimal.ZERO;
            default:
                return price.getPricePerDay() != null ? price.getPricePerDay() : BigDecimal.ZERO;
        }
    }

    public BigDecimal calculateTotalAmount(BigDecimal unitPrice, RentalOrder.RentalUnit unit,
                                            LocalDateTime startTime, LocalDateTime endTime) {
        if (unitPrice == null || unitPrice.compareTo(BigDecimal.ZERO) < 0) {
            return BigDecimal.ZERO;
        }

        long units = calculateRentalUnits(unit, startTime, endTime);
        BigDecimal amount = unitPrice.multiply(BigDecimal.valueOf(units));
        logger.debug("计算总金额: 单价 {} x 单位 {} = {}", unitPrice, units, amount);
        return amount;
    }

    private long calculateRentalUnits(RentalOrder.RentalUnit unit, LocalDateTime startTime, LocalDateTime endTime) {
        switch (unit) {
            case HOUR:
                return Math.max(1, ChronoUnit.HOURS.between(startTime, endTime));
            case DAY:
                return Math.max(1, ChronoUnit.DAYS.between(startTime, endTime));
            case WEEK:
                return Math.max(1, ChronoUnit.WEEKS.between(startTime, endTime));
            case MONTH:
                return Math.max(1, ChronoUnit.MONTHS.between(startTime, endTime));
            default:
                return Math.max(1, ChronoUnit.DAYS.between(startTime, endTime));
        }
    }

    private BigDecimal calculateExtraCharge(RentalOrder order) {
        LocalDateTime scheduledReturn = order.getReturnTime();
        LocalDateTime actualReturn = order.getActualReturnTime();

        if (actualReturn == null || actualReturn.isBefore(scheduledReturn) || actualReturn.isEqual(scheduledReturn)) {
            return BigDecimal.ZERO;
        }

        long extraDays = ChronoUnit.DAYS.between(scheduledReturn, actualReturn);
        if (extraDays == 0) {
            long extraHours = ChronoUnit.HOURS.between(scheduledReturn, actualReturn);
            if (extraHours > 0) {
                BigDecimal dailyRate = order.getUnitPrice();
                if (order.getRentalUnit() == RentalOrder.RentalUnit.HOUR) {
                    return dailyRate.multiply(BigDecimal.valueOf(extraHours));
                }
                
                BigDecimal hoursPerDay = BigDecimal.valueOf(24);
                BigDecimal extraDaysDecimal = BigDecimal.valueOf(extraHours)
                        .divide(hoursPerDay, 2, RoundingMode.HALF_UP);
                BigDecimal daysToCharge = new BigDecimal(Math.ceil(extraDaysDecimal.doubleValue()));
                
                return dailyRate.multiply(daysToCharge);
            }
            return BigDecimal.ZERO;
        }
        return order.getUnitPrice().multiply(BigDecimal.valueOf(extraDays));
    }

    private String generateOrderNumber() {
        return "RL" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 4).toUpperCase();
    }
}
