package validator

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"plant-care-reminder/internal/model"
)

var (
	validSunlightLevels = map[string]bool{
		"low":       true,
		"medium":    true,
		"high":      true,
		"full_sun":  true,
		"shade":     true,
		"partial":   true,
	}

	validOperations = map[string]bool{
		"water":     true,
		"fertilize": true,
		"prune":     true,
		"repot":     true,
	}

	validStatuses = map[string]bool{
		model.PlantStatusHealthy:   true,
		model.PlantStatusNeedsCare: true,
		model.PlantStatusSick:      true,
		model.PlantStatusDormant:   true,
	}

	dateRegex = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`)
)

type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

type ValidationErrors []*ValidationError

func (es ValidationErrors) Error() string {
	if len(es) == 0 {
		return ""
	}
	var msgs []string
	for _, e := range es {
		msgs = append(msgs, e.Error())
	}
	return strings.Join(msgs, "; ")
}

func (es ValidationErrors) HasErrors() bool {
	return len(es) > 0
}

func ValidatePlant(plant *model.CreatePlantRequest, defaultWater, defaultFertilize int, defaultSunlight string) ValidationErrors {
	var errors ValidationErrors

	if strings.TrimSpace(plant.Name) == "" {
		errors = append(errors, &ValidationError{
			Field:   "name",
			Message: "plant name is required",
		})
	} else if len(plant.Name) > 100 {
		errors = append(errors, &ValidationError{
			Field:   "name",
			Message: "plant name must be less than 100 characters",
		})
	}

	if strings.TrimSpace(plant.Species) == "" {
		errors = append(errors, &ValidationError{
			Field:   "species",
			Message: "plant species is required",
		})
	}

	if plant.WaterFrequency <= 0 {
		plant.WaterFrequency = defaultWater
	} else if plant.WaterFrequency > 365 {
		errors = append(errors, &ValidationError{
			Field:   "water_frequency_days",
			Message: "water frequency cannot exceed 365 days",
		})
	}

	if plant.FertilizeFreq <= 0 {
		plant.FertilizeFreq = defaultFertilize
	} else if plant.FertilizeFreq > 365 {
		errors = append(errors, &ValidationError{
			Field:   "fertilize_frequency_days",
			Message: "fertilize frequency cannot exceed 365 days",
		})
	}

	if strings.TrimSpace(plant.SunlightNeed) == "" {
		plant.SunlightNeed = defaultSunlight
	} else if !validSunlightLevels[strings.ToLower(plant.SunlightNeed)] {
		errors = append(errors, &ValidationError{
			Field:   "sunlight_need",
			Message: fmt.Sprintf("invalid sunlight level, must be one of: %s", getValidKeys(validSunlightLevels)),
		})
	}

	if len(plant.Notes) > 500 {
		errors = append(errors, &ValidationError{
			Field:   "notes",
			Message: "notes must be less than 500 characters",
		})
	}

	return errors
}

func ValidateUpdatePlant(req *model.UpdatePlantRequest) ValidationErrors {
	var errors ValidationErrors

	if req.Name != "" && len(req.Name) > 100 {
		errors = append(errors, &ValidationError{
			Field:   "name",
			Message: "plant name must be less than 100 characters",
		})
	}

	if req.WaterFrequency != nil {
		if *req.WaterFrequency <= 0 {
			errors = append(errors, &ValidationError{
				Field:   "water_frequency_days",
				Message: "water frequency must be positive",
			})
		} else if *req.WaterFrequency > 365 {
			errors = append(errors, &ValidationError{
				Field:   "water_frequency_days",
				Message: "water frequency cannot exceed 365 days",
			})
		}
	}

	if req.FertilizeFreq != nil {
		if *req.FertilizeFreq <= 0 {
			errors = append(errors, &ValidationError{
				Field:   "fertilize_frequency_days",
				Message: "fertilize frequency must be positive",
			})
		} else if *req.FertilizeFreq > 365 {
			errors = append(errors, &ValidationError{
				Field:   "fertilize_frequency_days",
				Message: "fertilize frequency cannot exceed 365 days",
			})
		}
	}

	if req.SunlightNeed != "" && !validSunlightLevels[strings.ToLower(req.SunlightNeed)] {
		errors = append(errors, &ValidationError{
			Field:   "sunlight_need",
			Message: fmt.Sprintf("invalid sunlight level, must be one of: %s", getValidKeys(validSunlightLevels)),
		})
	}

	if req.Status != "" && !validStatuses[req.Status] {
		errors = append(errors, &ValidationError{
			Field:   "status",
			Message: fmt.Sprintf("invalid status, must be one of: %s", getValidKeys(validStatuses)),
		})
	}

	if len(req.Notes) > 500 {
		errors = append(errors, &ValidationError{
			Field:   "notes",
			Message: "notes must be less than 500 characters",
		})
	}

	return errors
}

func ValidateCareOperation(req *model.CareOperationRequest) ValidationErrors {
	var errors ValidationErrors

	if !validOperations[req.Operation] {
		errors = append(errors, &ValidationError{
			Field:   "operation",
			Message: fmt.Sprintf("invalid operation, must be one of: %s", getValidKeys(validOperations)),
		})
	}

	if len(req.Operator) > 50 {
		errors = append(errors, &ValidationError{
			Field:   "operator",
			Message: "operator name must be less than 50 characters",
		})
	}

	if len(req.Notes) > 500 {
		errors = append(errors, &ValidationError{
			Field:   "notes",
			Message: "notes must be less than 500 characters",
		})
	}

	return errors
}

func ValidateDate(dateStr string) bool {
	if !dateRegex.MatchString(dateStr) {
		return false
	}
	_, err := time.Parse("2006-01-02", dateStr)
	return err == nil
}

func ValidateID(id string) bool {
	return strings.TrimSpace(id) != "" && len(id) <= 100
}

func ValidatePositiveInt(n int) bool {
	return n > 0
}

func ValidateStatus(status string) bool {
	return validStatuses[status]
}

func getValidKeys(m map[string]bool) string {
	var keys []string
	for k := range m {
		keys = append(keys, k)
	}
	return strings.Join(keys, ", ")
}
