#include <FnAttribute/FnAttribute.h>
#include <FnAttribute/FnDataBuilder.h>
#include <FnAttribute/FnGroupBuilder.h>
#include <FnGeolib/op/FnGeolibOp.h>
#include <FnGeolib/util/Path.h>
#include <FnGeolibServices/FnGeolibCookInterfaceUtilsService.h>
#include <FnGeolibServices/FnResolutionTable.h>
#include <FnGeolibServices/FnXFormUtil.h>
#include <FnPluginSystem/FnPlugin.h>


namespace {

class PassVisibility : public Foundry::Katana::GeolibOp
{
	public:
		static void setup(Foundry::Katana::GeolibSetupInterface& interface);
		static void cook(Foundry::Katana::GeolibCookInterface& interface);
	private:
		static void setPassVisibility(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation);
		static bool isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
			const std::string& rendererToTest);
		static const std::string getEnvVar(const std::string& envVarName,
			const std::string& defaultValue = "");
};


DEFINE_GEOLIBOP_PLUGIN(PassVisibility)

} // Katana anonymous namespace.

void registerPlugins()
{
    REGISTER_PLUGIN(PassVisibility, "PassVisibility", 0, 1);
}