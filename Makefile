compile:
	mvn -B -q clean compile -DskipTests

unit-tests:
	mvn -B $(MVN_VERBOSE_ARGS) test

static-analysis:
	$(call assert-set,SONAR_PASSWORD)
	mvn -B $(MVN_VERBOSE_ARGS) sonar:sonar -Dsonar.login=$(SONAR_PASSWORD) $(ADDITIONAL_ARGS)

package:
	mvn -B $(MVN_VERBOSE_ARGS) package -DskipTests

publish:
	@echo "publish"
