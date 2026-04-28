package com.example.vehiclerental.repository;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.Vehicle;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface RentalOrderRepository extends JpaRepository<RentalOrder, Long> {

    Optional<RentalOrder> findByOrderNumber(String orderNumber);

    List<RentalOrder> findByVehicle(Vehicle vehicle);

    List<RentalOrder> findByStatus(RentalOrder.OrderStatus status);

    List<RentalOrder> findByCustomerNameContaining(String customerName);

    List<RentalOrder> findByCustomerPhone(String customerPhone);

    @Query("SELECT r FROM RentalOrder r WHERE r.pickupTime BETWEEN :start AND :end")
    List<RentalOrder> findByPickupTimeBetween(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);

    @Query("SELECT r FROM RentalOrder r WHERE r.actualReturnTime BETWEEN :start AND :end")
    List<RentalOrder> findByActualReturnTimeBetween(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);

    @Query("SELECT r FROM RentalOrder r WHERE r.vehicle = :vehicle AND r.status IN :statuses")
    List<RentalOrder> findByVehicleAndStatusIn(@Param("vehicle") Vehicle vehicle, @Param("statuses") List<RentalOrder.OrderStatus> statuses);

    @Query("SELECT COUNT(r) FROM RentalOrder r WHERE r.status = :status")
    long countByStatus(@Param("status") RentalOrder.OrderStatus status);

    @Query("SELECT SUM(r.totalAmount) FROM RentalOrder r WHERE r.status = :status")
    java.math.BigDecimal sumTotalAmountByStatus(@Param("status") RentalOrder.OrderStatus status);

    @Query("SELECT r FROM RentalOrder r WHERE r.vehicle = :vehicle AND " +
           "((r.pickupTime <= :end AND r.returnTime >= :start) OR " +
           "(r.actualReturnTime IS NOT NULL AND r.actualReturnTime >= :start AND r.pickupTime <= :end)) AND " +
           "r.status IN :statuses")
    List<RentalOrder> findOverlappingOrders(@Param("vehicle") Vehicle vehicle,
                                              @Param("start") LocalDateTime start,
                                              @Param("end") LocalDateTime end,
                                              @Param("statuses") List<RentalOrder.OrderStatus> statuses);
}
