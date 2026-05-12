package com.example.vehiclerental.repository;

import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VehicleRepository extends JpaRepository<Vehicle, Long> {

    Optional<Vehicle> findByPlateNumber(String plateNumber);

    boolean existsByPlateNumber(String plateNumber);

    List<Vehicle> findByStatus(Vehicle.VehicleStatus status);

    List<Vehicle> findByVehicleType(VehicleType vehicleType);

    List<Vehicle> findByStatusIn(List<Vehicle.VehicleStatus> statuses);
}
