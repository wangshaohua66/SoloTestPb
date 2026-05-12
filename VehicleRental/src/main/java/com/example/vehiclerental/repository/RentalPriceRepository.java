package com.example.vehiclerental.repository;

import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.VehicleType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface RentalPriceRepository extends JpaRepository<RentalPrice, Long> {

    List<RentalPrice> findByVehicleType(VehicleType vehicleType);

    List<RentalPrice> findByVehicleTypeAndIsActiveTrue(VehicleType vehicleType);

    Optional<RentalPrice> findFirstByVehicleTypeAndIsActiveTrueOrderByEffectiveDateDesc(VehicleType vehicleType);

    @Query("SELECT rp FROM RentalPrice rp WHERE rp.vehicleType = :vehicleType AND rp.isActive = true " +
           "AND (rp.expiryDate IS NULL OR rp.expiryDate >= :date) " +
           "AND rp.effectiveDate <= :date ORDER BY rp.effectiveDate DESC")
    List<RentalPrice> findActivePricesForDate(@Param("vehicleType") VehicleType vehicleType,
                                                @Param("date") LocalDateTime date);
}
