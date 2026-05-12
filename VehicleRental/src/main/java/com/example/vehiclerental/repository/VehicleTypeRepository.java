package com.example.vehiclerental.repository;

import com.example.vehiclerental.entity.VehicleType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VehicleTypeRepository extends JpaRepository<VehicleType, Long> {

    Optional<VehicleType> findByName(String name);

    boolean existsByName(String name);

    List<VehicleType> findByAvailableTrue();
}
